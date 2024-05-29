# This is RESTful variation of Ticket System test task for SET University

Before the start:
 - 
- Install all packages

      pip install -r requirements.txt 
- !!! DON`T FORGET TO Create your own .env file and copy containment from .env.example

       

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
- Read documentation

      http://0.0.0.0:5000/api/docs/

Run tests:
 -
- I made a couple of them, and coverage will be not 100%)
    
      sudo docker-compose exec backend pytest
- or just 
    
      pytest
