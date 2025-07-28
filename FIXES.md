# Fixes

- static folder doesn't exist (not in root)
- allowed all hosts for the service
- updated the requirements (pip freeze >> requirements.txt)
- added poetry


## Deploy (without pressure):

0. Make updates and freeze requirements

With you virtual environment activated, run

```
pip freeze >> requirements.txt
```

And then push the updates to github

1. Sign in to Digital Ocean eg.

```
ssh root@ip
```

2. Navigate to project folder eg

```
cd WebApplications/geo_analytics
```

3. Pull updates eg

```
git pull origin main
```

> Alternatively, delete existing folder and clone the updated repository (project)
> eg `rm -rf /` and `git clone https://github.com/Chris-Daniel-2000/geo_analytics.git`

4. Create virtual environment and install dependecies (requirements)

```
python3 -m venv .venv 
```

and then activate it

```
source .venv/bin/activate
```

And then we can install the requirements

```
pip install requirements.txt
```

5. Run the project

```
nohup python run manage.py runserver 0.0.0.0:8000 &
```

6. See project in action

Visit ip:8000 in the browser