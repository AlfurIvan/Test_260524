# This is RESTful variation of Ticket System test task for SET University

Before the start:
 - 
- Install all packages

      pip install -r requirements.txt 

Start application:
 - 
- Build & run containers:

      docker compose up -d --build

- Clear db:

      docker compose exec backend python manage.py recreate_db
- Seed db:

      docker compose exec backend python manage.py seed
- Create your admin:

      docker compose exec backend python manage.py createsu

Run tests:
 -
- I made a couple of them, and coverage is not 100%)
    
      coming soon