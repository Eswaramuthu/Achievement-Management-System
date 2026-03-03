"""
AI Achievement Recommendation API

FastAPI server providing recommendation endpoints.
Runs as a standalone service alongside the existing AMS.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Optional

from recommendation_engine import (
    get_recommendations,
    get_student_profile,
    engine as recommendation_engine
)
from alumni_profiles import (
    ALUMNI_PROFILES,
    get_all_career_paths,
    get_alumni_by_career_path
)


# Create FastAPI app
app = FastAPI(
    title="AI Achievement Recommendation Service",
    description="Personalized achievement recommendations for students",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the recommendation dashboard"""
    dashboard_path = os.path.join(static_dir, "recommendation_dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return HTMLResponse(content="""
    <html>
        <head><title>AI Recommendation Service</title></head>
        <body style="font-family: Arial; padding: 40px;">
            <h1>🎯 AI Achievement Recommendation Service</h1>
            <p>API is running! Access endpoints:</p>
            <ul>
                <li><a href="/docs">/docs</a> - API Documentation</li>
                <li><a href="/api/recommendations/STUDENT_ID">/api/recommendations/{student_id}</a> - Get recommendations</li>
            </ul>
        </body>
    </html>
    """)


@app.get("/api/recommendations/{student_id}")
async def get_student_recommendations(
    student_id: str,
    career_goal: Optional[str] = Query(None, description="Target career path")
):
    """
    Get personalized achievement recommendations for a student.
    
    - **student_id**: Student's ID from the AMS database
    - **career_goal**: Optional target career path (e.g., "Data Science", "Web Development")
    
    Returns recommendations, similar alumni profiles, and insights.
    """
    result = get_recommendations(student_id, career_goal)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@app.get("/api/profile/{student_id}")
async def get_analyzed_profile(student_id: str):
    """
    Get analyzed student profile with achievement breakdown.
    
    Returns the student's achievement pattern analysis without recommendations.
    """
    profile = get_student_profile(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "student_id": profile.student_id,
        "name": profile.name,
        "department": profile.department,
        "total_achievements": profile.total_achievements,
        "achievement_types": profile.achievement_types,
        "skills": profile.skills,
        "positions": profile.positions,
        "predicted_career_paths": profile.predicted_career_paths
    }


@app.get("/api/alumni/similar/{student_id}")
async def find_similar_alumni(student_id: str, top_k: int = 3):
    """
    Find alumni with similar achievement profiles.
    
    - **student_id**: Student's ID
    - **top_k**: Number of similar alumni to return (default: 3)
    """
    profile = get_student_profile(student_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    
    similar = recommendation_engine.find_similar_alumni(profile, top_k)
    
    return {
        "student_id": student_id,
        "similar_alumni": [
            {
                "name": s["alumni"]["name"],
                "role": s["alumni"]["current_role"],
                "career_path": s["alumni"]["career_path"],
                "similarity": s["similarity"],
                "department": s["alumni"]["department"],
                "graduation_year": s["alumni"]["graduation_year"],
                "tips": s["alumni"]["tips"],
                "placement_package_lpa": s["alumni"]["placement_package_lpa"],
                "time_to_placement": f"{s['alumni']['time_to_placement_months']} months"
            }
            for s in similar
        ]
    }


@app.get("/api/career-paths")
async def list_career_paths():
    """List all available career paths for goal setting"""
    return {
        "career_paths": get_all_career_paths(),
        "alumni_count": {
            path: len(get_alumni_by_career_path(path))
            for path in get_all_career_paths()
        }
    }


@app.get("/api/alumni")
async def list_all_alumni(career_path: Optional[str] = None):
    """
    List alumni profiles, optionally filtered by career path.
    
    - **career_path**: Optional filter for specific career path
    """
    if career_path:
        alumni = get_alumni_by_career_path(career_path)
    else:
        alumni = ALUMNI_PROFILES
    
    return {
        "total": len(alumni),
        "alumni": [
            {
                "id": a["id"],
                "name": a["name"],
                "role": a["current_role"],
                "career_path": a["career_path"],
                "department": a["department"],
                "graduation_year": a["graduation_year"],
                "achievements_count": len(a["achievements"]),
                "placement_package_lpa": a["placement_package_lpa"]
            }
            for a in alumni
        ]
    }


@app.get("/api/stats")
async def get_system_stats():
    """Get overall statistics about the recommendation system"""
    count = len(ALUMNI_PROFILES)
    return {
        "total_alumni_profiles": count,
        "career_paths": len(get_all_career_paths()),
        "average_placement_package": round(
            sum(a["placement_package_lpa"] for a in ALUMNI_PROFILES) / count, 1
        ) if count > 0 else 0,
        "average_placement_time_months": round(
            sum(a["time_to_placement_months"] for a in ALUMNI_PROFILES) / count, 1
        ) if count > 0 else 0,
        "top_career_paths": [
            {"path": path, "count": len(get_alumni_by_career_path(path))}
            for path in get_all_career_paths()
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Recommendation Service"}


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 AI Achievement Recommendation Service")
    print("="*60)
    print("\n📍 Dashboard: http://localhost:5001/")
    print("📚 API Docs:  http://localhost:5001/docs")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
