# Smart Expense Buddy

Aplikacja webowa do wspólnego rozliczania wydatków w grupach. Umozliwia dodawanie wydatkow z roznymi metodami podzialu, automatyczne wyliczanie sald i minimalnych przelewow do rozliczenia, obsluge wielu walut z kursami NBP, wydatki cykliczne oraz powiadomienia w czasie rzeczywistym przez WebSocket.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy (async), PostgreSQL, Redis, APScheduler
- **Frontend:** React (TypeScript), Vite, Tailwind CSS, React Query, Axios
- **Infrastruktura:** Docker, Docker Compose, Nginx

## Funkcjonalnosci

- Rejestracja i logowanie (JWT)
- Tworzenie grup, dodawanie/usuwanie czlonkow, role (admin/member)
- Dodawanie wydatkow z podzialem: rowny, kwotowy, procentowy, udzialowy
- Salda grupy i sugerowane przelewy (algorytm minimalizacji transakcji)
- Rozliczenia (settle up) z historia
- Wydatki cykliczne (dzienne, tygodniowe, miesieczne)
- Konwerter walut (kursy z API NBP, cache Redis -> DB -> API)
- Powiadomienia na zywo (WebSocket)

## Wymagania

- Docker i Docker Compose

## Uruchomienie

```bash
docker compose up --build -d
```

Aplikacja bedzie dostepna pod:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs

## Uruchomienie lokalne (bez Dockera)

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Utworz plik `backend/.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/expense_tracker
SECRET_KEY=change-me-to-a-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

Uruchom migracje i serwer:

```bash
cd backend
python -m alembic upgrade head
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend lokalnie dziala na http://localhost:5173 i proxy'uje API na port 8000.

## Struktura projektu

```
backend/
  app/
    api/          # endpointy (auth, groups, expenses, settlements, currency, recurring, ws)
    core/         # konfiguracja, security (JWT, bcrypt)
    crud/         # operacje bazodanowe
    db/           # modele SQLAlchemy, sesja, migracje
    schemas/      # schematy Pydantic
    services/     # logika biznesowa (split, settlement, currency, scheduler, websocket)
  main.py

frontend/
  src/
    components/   # komponenty UI
    contexts/     # AuthContext
    hooks/        # React Query hooks
    lib/          # klient API, typy TypeScript
    pages/        # strony (login, register, dashboard, group)
```
