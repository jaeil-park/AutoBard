import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.series_engine import SeriesEngine

async def test_series():
    engine = SeriesEngine()
    topic = "전우치전"
    count = 3
    
    print(f"--- Testing Series Planning for: {topic} ({count} episodes) ---")
    plan = await engine.plan_series(topic, count)
    
    print(f"\n[Series Title]: {plan['series_title']}")
    for ep in plan['episodes']:
        print(f"  Ep {ep['ep_num']}: {ep['title']}")
        print(f"     Cliffhanger: {ep['cliffhanger']}")

    print("\n--- Testing Script Generation for Episode 1 ---")
    script = await engine.generate_episode_script(plan, 1)
    print(f"\n[Episode 1 Script Snippet]\n{script[:300]}...")
    
    # Check for tags
    if "[📝 NARRATIVE]" in script and "[🗨️ DIALOGUE]" in script:
        print("\n✅ Script format matches AutoBard standards.")
    else:
        print("\n❌ Script format missing tags.")

if __name__ == "__main__":
    asyncio.run(test_series())
