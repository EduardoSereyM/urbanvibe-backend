
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener URL de BDD
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada en .env")
    exit(1)

# Asegurar driver async
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def update_trigger():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    sql_command = """
    CREATE OR REPLACE FUNCTION public.handle_new_user()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $function$
    DECLARE
      gen_code TEXT;
    BEGIN
      -- Generar código UV-XXXXXX (6 caracteres alfanuméricos aleatorios)
      gen_code := 'UV-' || upper(substring(replace(gen_random_uuid()::text, '-', '') from 1 for 6));

      INSERT INTO public.profiles (
        id, 
        email, 
        username, 
        full_name, 
        avatar_url,
        role_id,
        referral_code
      )
      VALUES (
        new.id, 
        new.email, 
        -- Prioridad: 1. Metadata Username, 2. Metadata Full Name, 3. Email prefix
        COALESCE(
            new.raw_user_meta_data->>'username', 
            new.raw_user_meta_data->>'full_name', 
            split_part(new.email, '@', 1)
        ),
        COALESCE(new.raw_user_meta_data->>'full_name', ''),
        new.raw_user_meta_data->>'avatar_url',
        5, -- Default APP_USER role
        gen_code
      )
      ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        username = EXCLUDED.username,
        full_name = EXCLUDED.full_name,
        referral_code = COALESCE(profiles.referral_code, EXCLUDED.referral_code);
        
      RETURN new;
    END;
    $function$;
    """
    
    print("\n🚀 Ejecutando actualización del Trigger handle_new_user...")
    
    async with engine.begin() as conn:
        await conn.execute(text(sql_command))
        
    print("✅ Trigger actualizado correctamente.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_trigger())
