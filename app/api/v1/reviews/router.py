from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Review, ReviewReaction, ContentReport, Venue, Profile
from app.api.v1.reviews.schemas import ReviewReplyPayload, ReviewSchema, ReactionCreate, ContentReportCreate, ContentReportSchema, ReviewCreate
from app.services.venue_stats_service import update_venue_statistics

router = APIRouter()

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify venue exists
    result = await db.execute(select(Venue).where(Venue.id == payload.venue_id))
    venue = result.scalars().first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    new_review = Review(
        venue_id=payload.venue_id,
        user_id=current_user.id,
        general_score=payload.general_score,
        sub_scores=payload.sub_scores,
        comment=payload.comment,
        checkin_id=payload.checkin_id if hasattr(payload, 'checkin_id') else None, 
        media_urls=payload.media_urls
    )
    db.add(new_review)
    
    await update_venue_statistics(db, payload.venue_id)
    
    # --- Notificación al Dueño ---
    if venue.owner_id and venue.owner_id != current_user.id:
        from app.services.notifications import notification_service
        reviewer_name = current_user.username or current_user.display_name or "Un usuario"
        await notification_service.notify_venue_review(
            db=db,
            venue_name=venue.name,
            owner_id=venue.owner_id,
            reviewer_name=reviewer_name,
            rating=payload.general_score
        )
    
    await db.commit()
    await db.refresh(new_review)
    return new_review

@router.get("/venue/{venue_id}", response_model=List[ReviewSchema])
async def get_venue_reviews(
    venue_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    # Fetch reviews with deleted_at IS NULL
    query = select(Review).where(
        Review.venue_id == venue_id,
        Review.deleted_at == None
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    # Enrich with user data
    # The 'user' relationship is lazy by default in async. 
    # Use selectinload options or explicit join if needed for performance.
    # For now, let's do a quick fetch for users if not eager loaded, 
    # OR we can rely on eager loading if configured in model (lazy="selectin").
    # If not configured, accessing review.user might fail in async without await.
    # Let's assume we need to join Profile to be safe/efficient.
    
    # Efficient Query with Join
    # re-doing query to join Profile
    from sqlalchemy.orm import selectinload
    query = select(Review).options(selectinload(Review.user)).where(
        Review.venue_id == venue_id,
        Review.deleted_at == None
    ).order_by(Review.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    reviews = result.scalars().all()

    items = []
    for r in reviews:
        # r.user should be populated now
        if r.user:
            r.user_display_name = r.user.display_name or r.user.username or "Usuario"
        items.append(r)
        
    return items

# 1. Reply to Review (Venue Owner only)
# 1. Reply to Review (Venue Owner only)
@router.patch("/{review_id}/reply", response_model=ReviewSchema)
async def reply_to_review(
    review_id: UUID,
    payload: ReviewReplyPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalars().first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    # Check permissions: Current user must be owner of the venue
    result_venue = await db.execute(select(Venue).where(Venue.id == review.venue_id))
    venue = result_venue.scalars().first()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue associated with review not found")
        
    if venue.owner_id != current_user.id:
         # TODO: robust team check
         if getattr(current_user, 'role_id', None) != 1: # Assuming 1 is SUPER_ADMIN
            raise HTTPException(status_code=403, detail="Only the venue owner can reply to reviews")

    if review.owner_response:
        raise HTTPException(status_code=400, detail="Review already has a response. Edit not supported in this version.")

    review.owner_response = payload.response
    review.owner_responded_at = datetime.now()
    
    # We need the Profile ID of the responder
    result_profile = await db.execute(select(Profile).where(Profile.id == current_user.id))
    responder_profile = result_profile.scalars().first()
    
    if responder_profile:
        review.owner_responded_by = responder_profile.id
        
    await db.commit()
    await db.refresh(review)
    return review

# 2. React to Review (Helpful)
@router.post("/{review_id}/react", status_code=status.HTTP_200_OK)
async def react_to_review(
    review_id: UUID,
    payload: ReactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalars().first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot vote on your own review")
        
    result_reaction = await db.execute(select(ReviewReaction).where(
        ReviewReaction.review_id == review_id,
        ReviewReaction.user_id == current_user.id
    ))
    existing_reaction = result_reaction.scalars().first()

    if existing_reaction:
        # Toggle OFF (Remove reaction)
        await db.delete(existing_reaction)
        review.helpful_count = max(0, review.helpful_count - 1)
        action = "removed"
    else:
        # Toggle ON (Add reaction)
        new_reaction = ReviewReaction(
            review_id=review_id,
            user_id=current_user.id,
            reaction_type=payload.reaction_type
        )
        db.add(new_reaction)
        review.helpful_count += 1
        action = "added"
        
    await db.commit()
    return {"message": f"Reaction {action}", "helpful_count": review.helpful_count}

# 3. Report Content (Generic)
@router.post("/reports", response_model=ContentReportSchema, status_code=status.HTTP_201_CREATED)
async def report_content(
    payload: ContentReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_report = ContentReport(
        target_type=payload.target_type,
        target_id=payload.target_id,
        reporter_id=current_user.id,
        reason=payload.reason,
        details=payload.details
    )
    db.add(new_report)
    
    if payload.target_type == 'review':
        result = await db.execute(select(Review).where(Review.id == payload.target_id))
        review = result.scalars().first()
        if review:
            review.report_count += 1
    
    await db.commit()
    await db.refresh(new_report)
    return new_report
