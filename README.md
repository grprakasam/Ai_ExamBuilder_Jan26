# EduApp - NCDPI EOG Practice Test Generator

A comprehensive web application for creating North Carolina End-of-Grade (EOG) style practice tests aligned with NCDPI standards.

## Overview

EduApp helps students practice for EOG assessments by generating AI-powered, standards-aligned practice tests across multiple subjects and grade levels.

### Features

- **AI-Powered Question Generation**: Uses OpenAI to generate NCDPI-aligned questions
- **Multiple Subjects**: Mathematics, English, Science, and Social Studies
- **Grade Levels**: Supports grades 3-12
- **Question Types**: Multiple Choice (MCQ) and Open-Ended questions
- **Standards-Aligned**: Questions follow specific NCDPI standard focuses
- **PDF Export**: Download tests as PDF documents (requires WeasyPrint dependencies)
- **User Authentication**: Secure login and signup functionality
- **Real-time Feedback**: AI-powered feedback on student responses

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Development database (configurable to PostgreSQL)
- **OpenAI API**: AI-powered question generation
- **WeasyPrint**: PDF generation
- **Pydantic**: Data validation
- **JWT**: Authentication

### Frontend
- **React 19**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **TailwindCSS v4**: Utility-first CSS
- **Zustand**: State management
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Hook Form + Zod**: Form handling and validation

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
The `.env` file already exists. Update it with your OpenAI API key:
```env
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=dev_secret_key_for_testing_123
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

5. Start the backend server:
```bash
python run.py
```
Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
The `.env` file is already configured with:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

### Creating a Test

1. Open the application in your browser
2. Navigate to "Create Assessment"
3. Select:
   - Subject (Math, English, Science, Social Studies)
   - Grade Level (3-12)
   - Standard Focus
   - Number of Questions
   - Question Type (MCQ or Open-Ended)
   - Difficulty Level

4. Click "Generate with AI"
5. Once generated, you can:
   - Take the test immediately
   - Download as PDF (if WeasyPrint is configured)
   - View on the dashboard

### Taking a Test

1. From the dashboard, select a test
2. Answer the questions
3. Submit for grading
4. View results with AI-generated feedback

## Version Milestones

### Version 0.1 (Current)
- Basic test generation
- Input: grade level, subject, standard, number of questions, type, difficulty
- Output: Questions and answer key in PDF format

### Version 0.2 (Planned)
- Web application with UI
- Results, feedback, and suggestions
- Downloadable assessment results

### Version 0.3 (Planned)
- User authentication and authorization
- Login/logout with passcode validation

### Version 0.4 (Planned)
- Support for open-ended questions
- Real-time feedback and suggestions

## API Endpoints

### Tests
- `POST /api/v1/tests/generate` - Generate a new test
- `GET /api/v1/tests/{test_id}` - Get test details
- `GET /api/v1/tests/recent` - Get recent tests
- `POST /api/v1/tests/{test_id}/submit` - Submit test answers

### Auth
- `POST /api/v1/auth/signup` - Create new user
- `POST /api/v1/auth/login/access-token` - Login
- `GET /api/v1/auth/me` - Get current user

### Reports
- `GET /api/v1/reports/{test_id}/download` - Download test as PDF

## Troubleshooting

### WeasyPrint Warning
If you see a WeasyPrint warning, PDF generation will not work until you install the required system dependencies. Follow the instructions at:
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation

### OpenAI API Errors
Ensure your OpenAI API key is correctly set in `backend/.env` and you have sufficient credits.

### Database Errors
If you encounter database errors, delete the `sql_app.db` file and restart the backend to recreate the database.

### CORS Errors
The backend is configured to allow all origins in development. For production, update the CORS settings in `backend/app/main.py`.

## Development Notes

- The backend uses a custom UUID type that works with both SQLite and PostgreSQL
- Frontend uses Tailwind CSS v4 with the Vite plugin
- Demo user authentication is enabled by default (bypasses login)
- Database is automatically created on first run

## License

This project is for educational purposes.
