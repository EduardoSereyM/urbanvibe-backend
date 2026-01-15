import asyncio
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.models.gamification_advanced import Badge, Challenge, UserBadge, UserChallengeProgress
from app.models.profiles import Profile

async def seed_demo_data():
    async with AsyncSessionLocal() as db:
        print("[INFO] Starting Gamification Demo Seeding...")

        # 1. Create Badges
        # Badge 1: Primeros Usuarios (To be awarded immediately)
        res = await db.execute(select(Badge).where(Badge.name == "Primeros Usuarios"))
        badge_early = res.scalar_one_or_none()
        
        if not badge_early:
            print("[INFO] Creating Badge: Primeros Usuarios")
            badge_early = Badge(
                name="Primeros Usuarios",
                description="Por ser parte de la comunidad desde el inicio.",
                icon_url="https://img.icons8.com/color/96/guarantee.png", # Placeholder
                category="COMMUNITY"
            )
            db.add(badge_early)
            await db.flush()
        else:
            print("[INFO] Badge 'Primeros Usuarios' already exists.")

        # Badge 2: Insignia Pionero (Reward for Challenge)
        res = await db.execute(select(Badge).where(Badge.name == "Insignia Pionero"))
        badge_pionero = res.scalar_one_or_none()
        
        if not badge_pionero:
            print("[INFO] Creating Badge: Insignia Pionero")
            badge_pionero = Badge(
                name="Insignia Pionero",
                description="Completaste el reto de exploración inicial.",
                icon_url="https://img.icons8.com/color/96/rocket.png", # Placeholder
                category="EXPLORATION"
            )
            db.add(badge_pionero)
            await db.flush()
        else:
            print("[INFO] Badge 'Insignia Pionero' already exists.")

        # 2. Create Challenge
        # Challenge: Reto de Prueba
        res = await db.execute(select(Challenge).where(Challenge.code == "CHALLENGE_TEST_01"))
        challenge = res.scalar_one_or_none()
        
        if not challenge:
            print("[INFO] Creating Challenge: Reto de Prueba")
            challenge = Challenge(
                code="CHALLENGE_TEST_01",
                title="Reto de Prueba",
                description="Visita 3 lugares diferentes esta semana.",
                challenge_type="CHECKIN_COUNT",
                target_value=3,
                reward_points=500,
                reward_badge_id=badge_pionero.id,
                period_start=datetime.now(timezone.utc),
                period_end=datetime.now(timezone.utc) + timedelta(days=7),
                is_active=True
            )
            db.add(challenge)
            await db.flush()
        else:
             print("[INFO] Challenge 'Reto de Prueba' already exists.")

        # 3. Assign to Users
        # Get all users
        result_users = await db.execute(select(Profile))
        profiles = result_users.scalars().all()
        
        count_badges = 0
        count_challenges = 0

        for profile in profiles:
            # Assign Badge: Primeros Usuarios
            # Check if exists
            res_ub = await db.execute(select(UserBadge).where(
                UserBadge.user_id == profile.id,
                UserBadge.badge_id == badge_early.id
            ))
            if not res_ub.scalar_one_or_none():
                db.add(UserBadge(user_id=profile.id, badge_id=badge_early.id))
                count_badges += 1

            # Assign Active Challenge
            # Check if exists
            res_uc = await db.execute(select(UserChallengeProgress).where(
                UserChallengeProgress.user_id == profile.id,
                UserChallengeProgress.challenge_id == challenge.id
            ))
            if not res_uc.scalar_one_or_none():
                # Start with random progress for demo (0, 1 or 2)
                import random
                start_val = random.randint(0, 2)
                db.add(UserChallengeProgress(
                    user_id=profile.id, 
                    challenge_id=challenge.id,
                    current_value=start_val,
                    is_completed=False
                ))
                count_challenges += 1

        await db.commit()
        print(f"[OK] Finished! Awarded {count_badges} badges and started {count_challenges} challenges.")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
