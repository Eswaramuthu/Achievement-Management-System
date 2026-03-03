"""
Alumni Success Profiles Database

Contains sample alumni data representing successful career paths.
Used by the recommendation engine to find similar profiles and suggest achievements.
"""

# Sample successful alumni profiles with their achievement history and career outcomes
ALUMNI_PROFILES = [
    {
        "id": "ALUMNI_001",
        "name": "Priya Sharma",
        "graduation_year": 2022,
        "department": "CSE",
        "current_role": "Software Engineer at Google",
        "career_path": "Software Development",
        "achievements": [
            {"type": "Hackathon", "name": "Smart India Hackathon", "position": "1st", "level": "National"},
            {"type": "Hackathon", "name": "Google Code Jam", "position": "Top 100", "level": "International"},
            {"type": "Coding", "name": "LeetCode Contest", "position": "Top 5%", "level": "International"},
            {"type": "Project", "name": "AI Chatbot for Healthcare", "position": "Best Innovation", "level": "College"},
            {"type": "Paper", "name": "IEEE Conference on ML", "position": "Published", "level": "International"},
        ],
        "skills": ["Python", "Machine Learning", "System Design", "Cloud Computing", "DSA"],
        "time_to_placement_months": 2,
        "placement_package_lpa": 45,
        "tips": "Focus on competitive programming and build at least 2 major projects"
    },
    {
        "id": "ALUMNI_002", 
        "name": "Rahul Verma",
        "graduation_year": 2023,
        "department": "CSE",
        "current_role": "Data Scientist at Microsoft",
        "career_path": "Data Science",
        "achievements": [
            {"type": "Paper", "name": "International Journal of Data Science", "position": "Published", "level": "International"},
            {"type": "Paper", "name": "NeurIPS Workshop", "position": "Accepted", "level": "International"},
            {"type": "Hackathon", "name": "Analytics Vidhya Hackathon", "position": "2nd", "level": "National"},
            {"type": "Project", "name": "Predictive Maintenance System", "position": "1st", "level": "State"},
            {"type": "Internship", "name": "Microsoft Research Intern", "position": "Completed", "level": "International"},
        ],
        "skills": ["Python", "Deep Learning", "Statistics", "SQL", "TensorFlow", "Research"],
        "time_to_placement_months": 1,
        "placement_package_lpa": 42,
        "tips": "Publish research papers early and participate in ML competitions"
    },
    {
        "id": "ALUMNI_003",
        "name": "Ananya Reddy",
        "graduation_year": 2022,
        "department": "IT",
        "current_role": "Full Stack Developer at Amazon",
        "career_path": "Web Development",
        "achievements": [
            {"type": "Hackathon", "name": "AWS Hackathon", "position": "Winner", "level": "National"},
            {"type": "Project", "name": "E-commerce Platform", "position": "Best Project", "level": "College"},
            {"type": "Coding", "name": "HackerRank", "position": "5-star", "level": "International"},
            {"type": "Symposium", "name": "Web Dev Symposium", "position": "1st", "level": "State"},
            {"type": "Internship", "name": "Amazon SDE Intern", "position": "Completed", "level": "International"},
        ],
        "skills": ["JavaScript", "React", "Node.js", "AWS", "MongoDB", "System Design"],
        "time_to_placement_months": 1,
        "placement_package_lpa": 38,
        "tips": "Build full-stack projects and get cloud certifications"
    },
    {
        "id": "ALUMNI_004",
        "name": "Vikram Singh",
        "graduation_year": 2023,
        "department": "ECE",
        "current_role": "Embedded Systems Engineer at Intel",
        "career_path": "Embedded Systems",
        "achievements": [
            {"type": "Project", "name": "IoT Smart Home System", "position": "1st", "level": "National"},
            {"type": "Paper", "name": "IEEE Embedded Systems Conference", "position": "Published", "level": "International"},
            {"type": "Hackathon", "name": "Texas Instruments Innovation Challenge", "position": "Finalist", "level": "National"},
            {"type": "Symposium", "name": "Robotics Symposium", "position": "2nd", "level": "State"},
        ],
        "skills": ["C", "C++", "RTOS", "Arduino", "Raspberry Pi", "PCB Design"],
        "time_to_placement_months": 3,
        "placement_package_lpa": 28,
        "tips": "Work on hardware projects and get hands-on with microcontrollers"
    },
    {
        "id": "ALUMNI_005",
        "name": "Sneha Patel",
        "graduation_year": 2022,
        "department": "CSE",
        "current_role": "Product Manager at Flipkart",
        "career_path": "Product Management",
        "achievements": [
            {"type": "Hackathon", "name": "Product Case Competition", "position": "Winner", "level": "National"},
            {"type": "Project", "name": "User Analytics Dashboard", "position": "Best UI/UX", "level": "College"},
            {"type": "Symposium", "name": "Tech Management Symposium", "position": "1st", "level": "State"},
            {"type": "Internship", "name": "Flipkart PM Intern", "position": "Completed", "level": "National"},
            {"type": "Paper", "name": "Product Strategy Journal", "position": "Published", "level": "National"},
        ],
        "skills": ["Product Strategy", "Data Analysis", "SQL", "Figma", "A/B Testing"],
        "time_to_placement_months": 2,
        "placement_package_lpa": 32,
        "tips": "Develop business acumen alongside technical skills"
    },
    {
        "id": "ALUMNI_006",
        "name": "Arjun Kumar",
        "graduation_year": 2023,
        "department": "CSE",
        "current_role": "Security Engineer at Cisco",
        "career_path": "Cybersecurity",
        "achievements": [
            {"type": "Hackathon", "name": "CTF Competition", "position": "1st", "level": "National"},
            {"type": "Coding", "name": "Bug Bounty Program", "position": "Hall of Fame", "level": "International"},
            {"type": "Paper", "name": "Security Research Publication", "position": "Published", "level": "International"},
            {"type": "Project", "name": "Network Intrusion Detection", "position": "Best Innovation", "level": "State"},
        ],
        "skills": ["Network Security", "Penetration Testing", "Python", "Linux", "Cryptography"],
        "time_to_placement_months": 2,
        "placement_package_lpa": 35,
        "tips": "Participate in CTFs and contribute to security research"
    },
    {
        "id": "ALUMNI_007",
        "name": "Meera Iyer",
        "graduation_year": 2022,
        "department": "IT",
        "current_role": "DevOps Engineer at Netflix",
        "career_path": "DevOps/Cloud",
        "achievements": [
            {"type": "Project", "name": "CI/CD Pipeline Automation", "position": "Best Implementation", "level": "College"},
            {"type": "Hackathon", "name": "Cloud Native Hackathon", "position": "2nd", "level": "National"},
            {"type": "Coding", "name": "AWS Certified Solutions Architect", "position": "Certified", "level": "International"},
            {"type": "Symposium", "name": "DevOps Conference", "position": "Speaker", "level": "National"},
        ],
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "Linux"],
        "time_to_placement_months": 1,
        "placement_package_lpa": 40,
        "tips": "Get cloud certifications and build infrastructure projects"
    },
    {
        "id": "ALUMNI_008",
        "name": "Karthik Nair",
        "graduation_year": 2023,
        "department": "CSE",
        "current_role": "Mobile Developer at Swiggy",
        "career_path": "Mobile Development",
        "achievements": [
            {"type": "Project", "name": "Food Delivery App Clone", "position": "1st", "level": "College"},
            {"type": "Hackathon", "name": "Mobile App Challenge", "position": "Winner", "level": "State"},
            {"type": "Coding", "name": "Play Store Published Apps", "position": "3 Apps", "level": "International"},
            {"type": "Internship", "name": "Swiggy Android Intern", "position": "Completed", "level": "National"},
        ],
        "skills": ["Kotlin", "Flutter", "React Native", "Firebase", "REST APIs"],
        "time_to_placement_months": 2,
        "placement_package_lpa": 25,
        "tips": "Publish apps on Play Store and contribute to open source"
    },
]

# Achievement type importance weights for different career paths
CAREER_PATH_WEIGHTS = {
    "Software Development": {
        "Hackathon": 0.25,
        "Coding": 0.25,
        "Project": 0.20,
        "Paper": 0.10,
        "Internship": 0.15,
        "Symposium": 0.05,
    },
    "Data Science": {
        "Paper": 0.30,
        "Project": 0.20,
        "Hackathon": 0.15,
        "Coding": 0.15,
        "Internship": 0.15,
        "Symposium": 0.05,
    },
    "Web Development": {
        "Project": 0.30,
        "Hackathon": 0.20,
        "Coding": 0.20,
        "Internship": 0.15,
        "Symposium": 0.10,
        "Paper": 0.05,
    },
    "Cybersecurity": {
        "Hackathon": 0.25,
        "Coding": 0.20,
        "Paper": 0.20,
        "Project": 0.20,
        "Internship": 0.10,
        "Symposium": 0.05,
    },
    "DevOps/Cloud": {
        "Project": 0.25,
        "Coding": 0.25,
        "Hackathon": 0.15,
        "Internship": 0.20,
        "Symposium": 0.10,
        "Paper": 0.05,
    },
    "Mobile Development": {
        "Project": 0.30,
        "Coding": 0.20,
        "Hackathon": 0.20,
        "Internship": 0.15,
        "Symposium": 0.10,
        "Paper": 0.05,
    },
    "Product Management": {
        "Hackathon": 0.20,
        "Project": 0.25,
        "Internship": 0.25,
        "Paper": 0.10,
        "Symposium": 0.15,
        "Coding": 0.05,
    },
    "Embedded Systems": {
        "Project": 0.30,
        "Paper": 0.20,
        "Hackathon": 0.20,
        "Symposium": 0.15,
        "Internship": 0.10,
        "Coding": 0.05,
    },
}

# Achievement suggestions based on career goals
ACHIEVEMENT_SUGGESTIONS = {
    "Software Development": [
        {"type": "Hackathon", "name": "Smart India Hackathon", "reason": "National-level exposure and real problem-solving", "priority": "high"},
        {"type": "Coding", "name": "LeetCode/Codeforces Contests", "reason": "Improves DSA skills critical for interviews", "priority": "high"},
        {"type": "Project", "name": "Full-stack Application", "reason": "Demonstrates end-to-end development capability", "priority": "medium"},
        {"type": "Internship", "name": "Summer SDE Internship", "reason": "Industry experience significantly boosts placement", "priority": "high"},
    ],
    "Data Science": [
        {"type": "Paper", "name": "IEEE/ACM Conference Paper", "reason": "Research publications highly valued in ML roles", "priority": "high"},
        {"type": "Hackathon", "name": "Kaggle Competition", "reason": "Practical ML experience with real datasets", "priority": "high"},
        {"type": "Project", "name": "End-to-end ML Pipeline", "reason": "Shows ability to deploy ML models", "priority": "medium"},
        {"type": "Internship", "name": "Data Science Internship", "reason": "Industry experience with real data", "priority": "high"},
    ],
    "Web Development": [
        {"type": "Project", "name": "Production-ready Web App", "reason": "Portfolio projects are essential", "priority": "high"},
        {"type": "Hackathon", "name": "Web Development Hackathon", "reason": "Quick prototyping skills", "priority": "medium"},
        {"type": "Coding", "name": "Cloud Certification (AWS/GCP)", "reason": "Cloud skills are must-have", "priority": "high"},
        {"type": "Internship", "name": "Full Stack Internship", "reason": "Real-world codebase experience", "priority": "high"},
    ],
    "Cybersecurity": [
        {"type": "Hackathon", "name": "CTF Competition", "reason": "Practical security skills demonstration", "priority": "high"},
        {"type": "Coding", "name": "Bug Bounty Program", "reason": "Real vulnerability discovery experience", "priority": "high"},
        {"type": "Paper", "name": "Security Research", "reason": "Published research adds credibility", "priority": "medium"},
        {"type": "Project", "name": "Security Tool Development", "reason": "Shows practical application of knowledge", "priority": "medium"},
    ],
}

# Statistical insights for recommendations
STATISTICAL_INSIGHTS = {
    "Hackathon_National": "Students who won national hackathons got placed 40% faster on average",
    "Paper_International": "Alumni with international publications received 25% higher packages",
    "Internship_Tech": "Students with tech internships had 3x higher callback rate",
    "Coding_Competitive": "Top competitive programmers received 35% more interview calls",
    "Project_FullStack": "Full-stack project experience increased offer conversion by 50%",
    "Multiple_Types": "Students with 3+ achievement types had 60% higher placement rate",
}


def get_alumni_by_career_path(career_path: str) -> list:
    """Get alumni profiles matching a specific career path"""
    return [a for a in ALUMNI_PROFILES if a["career_path"] == career_path]


def get_all_career_paths() -> list:
    """Get list of all available career paths"""
    return list(set(a["career_path"] for a in ALUMNI_PROFILES))


def get_suggestions_for_career(career_path: str) -> list:
    """Get achievement suggestions for a career path"""
    return ACHIEVEMENT_SUGGESTIONS.get(career_path, ACHIEVEMENT_SUGGESTIONS["Software Development"])
