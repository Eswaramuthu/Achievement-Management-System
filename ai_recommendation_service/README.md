# AI Achievement Recommendation Service

A standalone AI-powered service that analyzes student achievements and provides personalized recommendations.

## Features

- 🎯 **Personalized Recommendations** - Based on achievement history and career goals
- 👥 **Alumni Comparison** - Compare with successful alumni profiles
- 📊 **Insights** - "Students with similar profiles got hired 40% faster"
- 🔒 **Non-invasive** - Works alongside existing AMS without modifications

## Quick Start

### 1. Install Dependencies

```powershell
cd ai_recommendation_service
pip install -r requirements.txt
```

### 2. Run the Service

```powershell
python api.py
```

The service will start on `http://localhost:5001`

### 3. Access the Dashboard

Open your browser and navigate to: `http://localhost:5001/`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommendations/{student_id}` | GET | Get personalized recommendations |
| `/api/profile/{student_id}` | GET | Get analyzed student profile |
| `/api/alumni/similar/{student_id}` | GET | Find similar alumni profiles |
| `/api/stats` | GET | Get system statistics |

## How It Works

1. **Reads** student achievements from existing `ams.db` (read-only)
2. **Analyzes** skills, achievement types, and patterns
3. **Matches** with successful alumni career paths
4. **Generates** personalized next-step recommendations

## Integration (Optional)

To link from the existing student dashboard, add this link:
```html
<a href="http://localhost:5001/?student_id={{student.id}}">AI Recommendations</a>
```
