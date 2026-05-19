import os
import re

filepath = r'c:\Users\DEV\Desktop\AchieveManagement\Achievement-Management-System\templates\teacher_new_2.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to remove the first broken form start up to the second form start.
# Looking at the file, the first form starts with:
# <form action="/teacher-new" method="POST" onsubmit="return validatePasswords(event)">
# Then it breaks at:
#                     <div class="input-box">
# 
#         /* Style for dropdown options */

# We can just extract everything before the first form, and everything after the second form ends.
# Better yet, let's just replace the entire content between `<div class="content">` and `</div>\n    </div>\n</body>`

new_content = re.sub(
    r'<div class="content">.*?<div class="back-link">',
    '''<div class="content">
            {% if error %}
            <div style="color: red; text-align: center; margin-bottom: 10px; font-weight: bold;">
                {{ error }}
            </div>
            {% endif %}
            <form action="/teacher-new" method="POST" onsubmit="return validatePasswords(event)">
                <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
                <div class="user-details">
                    <div class="input-box">
                        <span class="details">Full Name</span>
                        <input autocomplete="off" autofocus type="text" name="teacher_name"
                            placeholder="Enter your full name" required>
                    </div>

                    <div class="input-box">
                        <span class="details">Teacher ID</span>
                        <input autocomplete="off" type="text" name="teacher_id" placeholder="Enter your Teacher ID"
                            required>
                    </div>

                    <div class="input-box">
                        <span class="details">Email</span>
                        <input autocomplete="off" type="email" name="email" placeholder="Enter your email" required>
                    </div>

                    <div class="input-box">
                        <span class="details">Phone Number</span>
                        <input autocomplete="off" type="tel" name="phone_number" placeholder="Enter your phone number"
                            required>
                    </div>

                    <div class="input-box">
                        <span class="details">Password</span>
                        <input autocomplete="off" type="password" id="password" name="password"
                            placeholder="Enter your Password" required>
                    </div>

                    <div class="input-box">
                        <span class="details">Confirm Password</span>
                        <input type="password" id="confirm-password" placeholder="Confirm your password" required>
                        <small id="password-message" style="font-size: 14px;"></small>
                    </div>

                    <div class="input-box">
                        <span class="details">Gender</span>
                        <select name="teacher_gender" required>
                            <option disabled selected value="">Gender</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>

                    <div class="input-box">
                        <span class="details">Department</span>
                        <select name="teacher_dept" required>
                            <option disabled selected value="">Department</option>
                            <option value="CSE">CSE</option>
                            <option value="CSE(E Tech)">CSE(E Tech)</option>
                            <option value="ECE">ECE</option>
                            <option value="MECH">MECH</option>
                        </select>
                    </div>

                    <div class="input-box" style="margin-top: 20px; width: 100%;">
                        <span class="details">Teacher Code <small>(Required for verification)</small></span>
                        <input autocomplete="off" type="password" name="teacher_code" placeholder="Enter Teacher Code"
                            required style="width: 100%;">
                    </div>
                </div>

                <div class="button">
                    <input type="submit" value="Register">
                </div>
            </form>

            <div class="back-link">''',
    content,
    flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Done")
