from typing import Any, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from uuid import UUID

from app.api import deps
from app.models.venue_team import VenueTeam
from app.models.profiles import Profile
from app.schemas.venue_team import TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse

router = APIRouter()

async def check_venue_ownership(
    venue_id: UUID, 
    user_id: UUID, 
    db: AsyncSession
) -> bool:
    """Valida si el usuario es dueño del venue."""
    result = await db.execute(
        text("SELECT 1 FROM public.venues WHERE id = :venue_id AND owner_id = :user_id"),
        {"venue_id": venue_id, "user_id": user_id}
    )
    return result.scalar() is not None

@router.post("/{venue_id}/team", response_model=TeamMemberResponse)
async def add_team_member(
    venue_id: UUID,
    member_in: TeamMemberCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[deps.Profile, Depends(deps.get_current_user)],
):
    """
    Alta de Personal B2B (Onboarding Inteligente).
    1. Verifica si el usuario actual es dueño del local.
    2. Busca si el email ya existe en perfiles.
       - Si existe: lo vincula.
       - Si no existe: (TODO: Integrar Auth Service) por ahora ERROR 404 informando flujo mock.
    3. Crea la relación en venue_team.
    """
    # 1. Tenant Isolation: Check Ownership
    is_owner = await check_venue_ownership(venue_id, current_user.id, db)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar el equipo de este local."
        )

    # 2. Check Role Validity (Solo Staff=4 o Manager=3)
    if member_in.role_id not in [3, 4]:
        raise HTTPException(status_code=400, detail="Rol inválido. Solo Staff (4) o Manager (3).")

    # 3. Smart User Lookup
    # Buscamos por email en profiles (gracias al refactor anterior el email vive aquí)
    result = await db.execute(select(Profile).where(Profile.email == member_in.email))
    existing_user = result.scalars().first()
    
    target_user_id = None
    
    if existing_user:
        target_user_id = existing_user.id
        print(f"✅ Usuario existente encontrado: {existing_user.id}")
    else:
        # Scenario A: User does not exist -> Create auto-account
        from app.core.supabase_admin import get_supabase_admin
        
        print(f"🆕 Usuario nuevo ({member_in.email}). Creando cuenta automática...")
        supabase_admin = get_supabase_admin()
        
        # Temp password (In prod: Generate random and email it)
        temp_password = "UrbanVibeMember123!" 
        
        try:
            # 1. Create Identity in Auth
            auth_response = supabase_admin.auth.admin.create_user({
                "email": member_in.email,
                "password": temp_password,
                "email_confirm": True, # Auto-confirm
                "user_metadata": {
                    "full_name": member_in.full_name,
                    "username": member_in.email.split("@")[0], # Auto-generate username from email
                    "app_role": "APP_USER" # Default global role
                }
            })
            
            new_user_id = UUID(auth_response.user.id)
            print(f"✅ Auth User creado: {new_user_id}")
            
            # 2. Create local Profile (Data Mirroring)
            new_profile = Profile(
                id=new_user_id,
                email=member_in.email,
                full_name=member_in.full_name,
                username=member_in.email.split("@")[0], # Auto-generate unique username (assumed unique here or DB will error)
                role_id=5, # Default to APP_USER globally
                display_name=member_in.full_name.split(" ")[0] if " " in member_in.full_name else member_in.full_name
            )
            db.add(new_profile)
            await db.commit() # Commit profile first to satisfy FK
            
            target_user_id = new_user_id
            
            # Mock Notification
            print(f"📧 [MOCK EMAIL] To: {member_in.email} | Subject: Bienvenido al equipo! | Body: Tu contraseña temporal es: {temp_password}")
            
        except Exception as e:
            print(f"❌ Error creando usuario automático: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creando usuario automático: {str(e)}"
            )

    # 4. Check if already in team
    existing_membership = await db.execute(
        select(VenueTeam).where(
            VenueTeam.venue_id == venue_id,
            VenueTeam.user_id == target_user_id
        )
    )
    membership = existing_membership.scalars().first()
    
    if membership:
        if not membership.is_active:
             # Reactivar
            membership.is_active = True
            membership.role_id = member_in.role_id
            await db.commit()
            await db.refresh(membership)
            return membership
        else:
            raise HTTPException(status_code=400, detail="El usuario ya es parte activa del equipo.")

    # 5. Create Link
    new_member = VenueTeam(
        venue_id=venue_id,
        user_id=target_user_id,
        role_id=member_in.role_id,
        is_active=True
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    
    # Enrich response manually for now
    new_member.full_name = existing_user.full_name
    new_member.email = existing_user.email
    
    return new_member

@router.get("/{venue_id}/team", response_model=List[TeamMemberResponse])
async def list_team_members(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[deps.Profile, Depends(deps.get_current_user)],
):
    # Tenant Isolation
    is_owner = await check_venue_ownership(venue_id, current_user.id, db)
    if not is_owner:
        raise HTTPException(status_code=403, detail="No autorizado.")

    query = text("""
        SELECT vt.*, p.full_name, p.email, r.name as role_name
        FROM public.venue_team vt
        JOIN public.profiles p ON vt.user_id = p.id
        JOIN public.app_roles r ON vt.role_id = r.id
        WHERE vt.venue_id = :venue_id
          AND vt.is_active = true
    """)
    
    result = await db.execute(query, {"venue_id": venue_id})
    members = result.mappings().all()
    return members

@router.patch("/{venue_id}/team/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    venue_id: UUID,
    member_id: UUID, # Este es el User ID del miembro, no el ID de la tabla team
    member_update: TeamMemberUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[deps.Profile, Depends(deps.get_current_user)],
):
    """
    Baja de Personal (Soft Delete) o Cambio de Rol.
    """
    # Tenant Isolation
    is_owner = await check_venue_ownership(venue_id, current_user.id, db)
    if not is_owner:
        raise HTTPException(status_code=403, detail="No autorizado.")

    # Prevent Self-Destruct? (Owner removing themselves if they are in the list)
    if member_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo desde aquí.")

    # Find membership
    query = select(VenueTeam).where(
        VenueTeam.venue_id == venue_id,
        VenueTeam.user_id == member_id
    )
    result = await db.execute(query)
    membership = result.scalars().first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Miembro no encontrado en este equipo.")

    # Apply updates
    if member_update.role_id is not None:
        membership.role_id = member_update.role_id
    if member_update.is_active is not None:
        membership.is_active = member_update.is_active

    await db.commit()
    await db.refresh(membership)
    return membership
