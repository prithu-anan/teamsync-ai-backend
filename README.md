## Project Setup

* Clone the repository

```bash
git clone https://github.com/suhashines/teamysnc-ai-backend.git
cd teamysnc-ai-backend
```

* Create and activate virtual environment

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

* Install the dependencies

```bash
pip install -r requirements.txt
```

* Create a .env file with the following credential - 

```bash
DATABASE_URL=postgresql://postgres:123@localhost:5433/postgres
```

* Make sure the postgres docker service is running
* Then run fast api backend

```bash
uvicorn app.main:app --reload
```

- Health check 

[Click on this link]( http://localhost:8000/health)

- You'll see
