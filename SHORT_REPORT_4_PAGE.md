# AI Resume Maker - Short Report (Submission Version)

## Abstract

The **AI Resume Maker** is a web-based application that helps users create ATS-friendly resumes quickly using structured input and AI-assisted text generation. The project is built using **Flask (Python)** for the backend and **HTML/CSS/JavaScript** for the frontend.  

Users enter profile details such as personal information, summary, skills, work experience, education, projects, and certifications. The application then generates a professional resume in plain text format. If AI generation is unavailable due to API or network issues, the system uses a fallback generator to ensure uninterrupted usability.  

In addition to generation, the project supports resume export in multiple formats: **TXT, PDF, DOCX, JPG, and PNG**. The UI is designed with a smooth, modern, and colorful theme, offering an improved user experience through responsive layout, transitions, and clear status feedback.

---

## 1. Introduction

In today's competitive job market, candidates need resumes that are clear, relevant, and optimized for Applicant Tracking Systems (ATS). Many users struggle with resume writing, formatting, and selecting impactful content for their target roles. The AI Resume Maker addresses this challenge by combining user input with AI-guided generation to produce structured and professional resume content.

The project focuses on three main goals:

1. **Ease of use** - users can generate resumes through a simple form.
2. **Automation** - AI support reduces the effort required to write polished content.
3. **Practical output** - downloadable files in common formats improve usability for real applications.

This report presents the project design, implementation, features, testing status, and future scope.

---

## 2. Problem Statement

Many students and job seekers face the following issues:

- Difficulty in writing concise and professional resume points.
- Lack of role-specific resume content.
- Limited access to tools that export in multiple useful formats.
- Poorly designed or confusing resume builders.

Existing solutions are often either complex, paid, or do not provide AI fallback reliability. Hence, a lightweight, modern, and practical resume generation system was needed.

---

## 3. Objectives

The key objectives of this project were:

- To build a lightweight web application for resume generation.
- To integrate AI-based content generation using Gemini API.
- To provide a fallback generation mode when AI is unavailable.
- To support downloads in **PDF, DOCX, JPG, PNG, and TXT** formats.
- To design an attractive and smooth user interface.
- To keep the architecture simple for future extension and deployment.

---

## 4. Technology Stack

### 4.1 Backend
- **Python 3**
- **Flask**

### 4.2 Frontend
- **HTML5**
- **CSS3**
- **Vanilla JavaScript**

### 4.3 AI Integration
- **Google Gemini API** (`gemini-1.5-flash`)

### 4.4 File Generation Libraries
- **reportlab** (PDF)
- **python-docx** (DOCX)
- **Pillow** (JPG, PNG)

### 4.5 Development Environment
- Windows + PowerShell
- Localhost execution (`http://localhost:5000`)

---

## 5. System Design

### 5.1 High-Level Workflow

1. User opens the website.
2. User enters resume details in form fields.
3. User clicks **Generate Resume**.
4. Frontend sends input data to backend API.
5. Backend generates resume using:
   - Gemini API (if valid key and response available), or
   - fallback template generator.
6. Generated resume text is displayed on screen.
7. User can copy text or download in required format.

### 5.2 Core Modules

#### A) Input Module
Collects:
- Name, role, email, phone, location
- LinkedIn/portfolio
- Summary, skills, experience
- Projects, education, certifications

#### B) Generation Module
- Builds a structured prompt for ATS-friendly output.
- Calls Gemini API using secure key from environment variables.
- Falls back to deterministic resume template if AI fails.

#### C) Export Module
Converts generated text into:
- `.pdf` using reportlab
- `.docx` using python-docx
- `.png` and `.jpg` using Pillow
- `.txt` using browser blob download

#### D) UI Module
- Glassmorphism-inspired design
- Responsive grid layout
- Button interactions and smooth transitions
- Loading/success/error status messages

---

## 6. API Endpoints

### 6.1 `GET /`
Serves the main web interface (`index.html`).

### 6.2 `POST /api/generate-resume`
**Purpose:** Generate resume content from user input.  

**Input:** JSON form data  
**Output:** JSON:
- `resume`: generated text
- `source`: `gemini` or `fallback`  

**Validation:** Requires at least `fullName` and `targetRole`.

### 6.3 `POST /api/download-resume`
**Purpose:** Download generated resume in requested format.  

**Input:**
- `resume` (text)
- `format` (`pdf`, `docx`, `jpg`, `png`)
- `fileName` (optional)

**Output:** File attachment response.

---

## 7. Features Implemented

The final implementation includes:

1. AI-powered resume generation.
2. Local fallback generation for reliability.
3. Modern and colorful UI with smooth effects.
4. Copy-to-clipboard support.
5. Multi-format downloads:
   - TXT
   - PDF
   - DOCX
   - JPG
   - PNG
6. Input validation for required fields.
7. Clear status communication for user actions.

---

## 8. Testing and Validation

Functional testing was performed for:

- Resume generation route and error handling.
- Fallback behavior when AI result is unavailable.
- Download route for all supported file formats.
- Frontend interactions: generate, copy, download buttons.
- Responsive behavior on smaller screen widths.

Observed result:
- APIs return successful responses for all supported formats.
- Downloads work correctly with valid generated content.
- The UI remains stable and usable across interactions.

---

## 9. Results

The project successfully delivers a complete resume generation workflow:

- Users can generate professional resume content quickly.
- The fallback mechanism ensures uninterrupted operation.
- Multi-format export makes output practical for different use cases.
- The polished UI improves overall usability and presentation quality.

This demonstrates that a lightweight Flask app can effectively combine AI integration, UX design, and document generation into a single useful productivity tool.

---

## 10. Limitations

Current limitations include:

- AI quality depends on API key validity, quota, and access permissions.
- Generated output is plain text (not a fully styled template preview).
- Image export is text-rendered and minimal in formatting.
- No user authentication or cloud persistence yet.

---

## 11. Future Scope

The following improvements can enhance the project further:

- Add multiple styled resume templates.
- Introduce role-specific keyword optimization for ATS scoring.
- Build rich PDF template formatting and section styling.
- Add user login and resume history storage.
- Deploy to cloud with stable production URL.
- Add one-click import from LinkedIn/profile data.

---

## 12. Conclusion

The AI Resume Maker project meets its primary objective of creating a simple, intelligent, and reliable resume generation platform. It integrates AI-based text generation with robust fallback logic and supports practical multi-format downloads. With a modern, responsive interface and clean backend APIs, the system is suitable for academic submission and can be expanded into a production-ready product with template enhancements, persistence, and deployment.

---

## References

1. Flask Documentation: https://flask.palletsprojects.com/
2. Google Gemini API Documentation: https://ai.google.dev/
3. ReportLab Documentation: https://www.reportlab.com/documentation/
4. python-docx Documentation: https://python-docx.readthedocs.io/
5. Pillow Documentation: https://pillow.readthedocs.io/
