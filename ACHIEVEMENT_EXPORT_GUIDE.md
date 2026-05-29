# Achievement Card Export Feature - Implementation Guide

## Overview

The Achievement Card Export feature allows students to generate and share professional achievement cards (PNG/PDF) with QR codes that link to publicly verifiable achievement records.

---

## 🔧 Integration Steps

### Step 1: Add Scripts and Styles to Your Base Template

In `templates/base.html` or `templates/student_dashboard.html`, add these in the `<head>` section:

```html
<!-- Achievement Export Styles -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/achievement-card.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/achievement-share.css') }}">

<!-- Achievement Export Scripts (at end of body) -->
<script src="{{ url_for('static', filename='js/achievement-share.js') }}"></script>
```

### Step 2: Add Share Button to Achievement Cards

In any template where you display achievements (e.g., `templates/student_achievements.html`), add this button to each achievement card:

```html
<!-- Inside your achievement card HTML -->
<div class="achievement-actions">
    <!-- Existing buttons -->
    <a href="#" class="action-button download-btn">Download Certificate</a>
    
    <!-- NEW: Share button -->
    <button class="action-button share-btn" onclick="shareAchievement({{ achievement.id }})">
        🔗 Share Achievement
    </button>
</div>
```

Or use this styled version:

```html
<button 
    class="btn btn-share" 
    onclick="shareAchievement({{ achievement.id }})"
    title="Generate shareable card and verification link"
>
    <span class="btn-icon">🔗</span>
    Share Achievement
</button>
```

### Step 3: Add Share Button CSS

Add this to your existing CSS file or create a new stylesheet:

```css
.share-btn {
    background-color: #4CAF50;
    color: white;
    padding: 8px 12px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.3s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.share-btn:hover {
    background-color: #45a049;
}

.btn-share {
    background: linear-gradient(135deg, #00d084 0%, #00a85c 100%);
    color: white;
    padding: 10px 16px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.btn-share:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 208, 132, 0.3);
}

.btn-icon {
    font-size: 16px;
}
```

---

## 📁 File Structure

```
Achievement-Management-System/
├── app.py                                    # New routes added
├── requirements.txt                          # Added: qrcode[pil]
├── utils/
│   └── qr_handler.py                        # NEW: QR code generation
├── static/
│   ├── js/
│   │   ├── achievement-export.js            # NEW: PNG/PDF export logic
│   │   └── achievement-share.js             # NEW: Share modal component
│   └── css/
│       ├── achievement-card.css             # NEW: Card styling
│       └── achievement-share.css            # NEW: Modal styling
└── templates/
    ├── achievement_export.html              # NEW: Export page
    ├── verify_achievement.html              # NEW: Verification page
    └── student_achievements.html            # MODIFIED: Add share button
```

---

## 🚀 Usage Flow

### For Students:

1. **View Achievement** - Student opens their achievement dashboard
2. **Click Share Button** - Clicks "Share Achievement" on any achievement card
3. **Choose Action** - Modal opens with options:
   - 🎫 **Export Card** - Opens export page in new window for PNG/PDF download
   - 🔗 **Verify Link** - Copies the public verification URL
   - in **LinkedIn** - Opens LinkedIn share dialog
   - 𝕏 **Twitter** - Opens Twitter share dialog
   - 📋 **Copy Link** - Copies the verification link to clipboard

4. **Share** - Student posts on social media, downloads card, or shares link

### For Public Users:

1. **Receive Link/QR Code** - User receives verification URL or scans QR code
2. **View Verification Page** - Opens public verification page (no login required)
3. **Verify Achievement** - See achievement details, security info, and metadata
4. **Share Further** - Can print, screenshot, or share from verification page

---

## 🔐 Security Features

### Access Control

- ✅ **Export Route** (`/export-achievement/<id>`) - Only authenticated students can export their own achievements
- ✅ **API Route** (`/api/achievement/<id>`) - Only students can fetch their own achievement JSON
- ✅ **Verification Route** (`/verify-achievement/<id>`) - Public access (no auth), but read-only

### Data Protection

- ✅ **QR Code** - Encodes verification URL only, no sensitive data
- ✅ **Certificate Hash** - Recorded to detect duplicates and modifications
- ✅ **Ownership Verification** - Backend checks that student_id matches session

### Privacy

- ✅ **Public Data Only** - Verification page shows only achievement details, not passwords/emails
- ✅ **HTTPS in Production** - QR codes use HTTPS scheme on production
- ✅ **No API Key Exposure** - No sensitive keys in frontend code

---

## 🎨 Customization

### Change Card Colors

Edit `static/css/achievement-card.css`:

```css
:root {
    --card-bg: #ffffff;
    --card-accent: #d40000;           /* Main accent color */
    --card-accent-light: rgba(212, 0, 0, 0.1);
    --card-shadow: rgba(0, 0, 0, 0.12);
}
```

### Modify Card Layout

Edit `templates/achievement_export.html` to add/remove fields:

```html
<!-- Example: Add team size if present -->
{% if achievement.team_size %}
<div class="detail-row">
    <label>Team Size:</label>
    <span class="detail-value">{{ achievement.team_size }} members</span>
</div>
{% endif %}
```

### Change Export Dimensions

Edit `static/js/achievement-export.js`:

```javascript
this.cardWidth = 600;   // Change to different width (pixels)
this.cardHeight = 800;  // Change to different height (pixels)
this.dpi = 2;           // Change to 1 for normal DPI, 3 for ultra-high quality
```

### Add Custom Fields to QR Code

Edit `utils/qr_handler.py` to modify URL format:

```python
# Current: https://domain.com/verify-achievement/{id}
# Custom: https://domain.com/verify-achievement/{id}?student={student_id}&event={event}
```

---

## 🧪 Testing Checklist

### Functionality Testing

- [ ] Click "Share Achievement" button
- [ ] Modal opens correctly
- [ ] Export Card button opens new window
- [ ] PNG export downloads successfully
- [ ] PDF export generates without errors
- [ ] Verify Link copies correct URL
- [ ] LinkedIn share works
- [ ] Twitter share works
- [ ] Copy link copies correct URL

### Security Testing

- [ ] Logged-in student can only export own achievements
- [ ] Guest can't access `/export-achievement/` routes
- [ ] Guest can access `/verify-achievement/` routes
- [ ] QR code links to correct verification page
- [ ] Verification page shows correct data

### Responsive Testing

- [ ] Modal works on mobile (< 600px)
- [ ] Card exports correctly on mobile
- [ ] Verification page responsive on all devices
- [ ] Touch-friendly button sizes

### Dark/Light Mode Testing

- [ ] Modal respects theme toggle
- [ ] Card colors correct in both modes
- [ ] Verification page shows correct theme
- [ ] QR code visible in both modes

### Browser Testing

- [ ] Chrome/Edge (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Mobile browsers (Safari iOS, Chrome Android)

---

## 📊 Database Schema (No Changes Needed)

The feature uses existing achievement table:

```sql
achievements:
- id (INTEGER) - Achievement ID (used in URLs)
- student_id (TEXT) - Foreign key to student
- achievement_type (TEXT) - Type of achievement
- event_name (TEXT) - Event name
- achievement_date (DATE) - Date of achievement
- organizer (TEXT) - Organizing body
- position (TEXT) - Position/rank achieved
- achievement_description (TEXT) - Description
- certificate_hash (TEXT) - Hash for duplicate detection
- created_at (TIMESTAMP) - Record creation time
```

✅ **No database migrations needed** - All fields already exist

---

## 🐛 Troubleshooting

### "html2canvas is not defined"

**Problem**: Export button doesn't work
**Solution**: Ensure CDN scripts are loaded in `achievement_export.html`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

### QR Code Not Generating

**Problem**: QR code shows as broken image
**Solution**: Install qrcode package:
```bash
pip install qrcode[pil]
```

### Export URL Incorrect

**Problem**: Verification link is HTTP instead of HTTPS
**Solution**: Update `get_verification_url()` in `utils/qr_handler.py`:
```python
scheme = "https" if "localhost" not in request_host else "http"
```

### Modal Not Appearing

**Problem**: Share modal doesn't open when button clicked
**Solution**: Ensure JavaScript is loaded in correct order:
1. Base scripts (script.js)
2. Achievement share module (achievement-share.js)
3. Inline HTML with onclick handlers

---

## 📈 Performance Considerations

### Optimization Tips

1. **QR Code Generation**: Happens server-side, lightweight (< 1ms per QR)
2. **Image Export**: html2canvas runs client-side, ~1-3 seconds per card
3. **PDF Generation**: jsPDF runs client-side, ~2-5 seconds per PDF
4. **Database Queries**: Indexed by `id` and `student_id` for O(1) lookups

### Caching Strategies

- QR codes: Generate on-demand (small data, fast generation)
- Achievement data: Cached in session for repeated exports
- Static assets: CDN-friendly (external libraries)

### File Sizes

- achievement-export.js: ~8 KB
- achievement-share.js: ~6 KB
- achievement-card.css: ~12 KB
- achievement-share.css: ~6 KB
- **Total**: ~32 KB (gzip: ~8 KB)

---

## 🔮 Future Enhancements

### Planned Features

1. **Batch Export** - Export multiple achievements at once
2. **Custom Branding** - Student logo on export card
3. **Analytics** - Track verification link clicks
4. **Sharing History** - Show where achievements were shared
5. **Social Media Preview** - Open Graph tags on verification page
6. **Certificate Templates** - Different card designs to choose from
7. **Email Sharing** - Send achievement card via email
8. **Watermark** - Add institution watermark to exports

### Integration Ideas

- LinkedIn Skill Endorsements
- Resume Builder
- GitHub Gists
- Medium Articles
- Personal Website Widget

---

## 📚 API Reference

### Routes

#### `GET /api/achievement/<id>`
**Authentication**: Required (Student only - own achievements)
**Returns**: JSON with achievement data + QR code

```json
{
    "id": 123,
    "event_name": "CodeFest 2025",
    "position": "First Place",
    "student_name": "John Doe",
    "qr_code": "data:image/png;base64,...",
    "verification_url": "https://domain.com/verify-achievement/123",
    ...
}
```

#### `GET /verify-achievement/<id>`
**Authentication**: Not required (Public)
**Returns**: HTML verification page

#### `GET /export-achievement/<id>`
**Authentication**: Required (Student only - own achievements)
**Returns**: HTML export page with download controls

### Utility Functions (JavaScript)

```javascript
// Open share modal
shareAchievement(achievementId);

// Manual export (if needed)
const exporter = new AchievementExporter();
await exporter.exportPNG();
await exporter.exportPDF();
```

---

## 📞 Support & Contributing

For issues, suggestions, or contributions:

1. **Report Bug**: Create issue on GitHub
2. **Suggest Feature**: Open discussion
3. **Submit PR**: Follow existing code style
4. **Security Issue**: Email admin@institution.com

---

## 📄 License

This feature is part of the Achievement Management System and follows the same license.

---

**Version**: 1.0
**Last Updated**: May 2026
**Compatibility**: Python 3.8+, Flask 2.0+, Modern browsers
