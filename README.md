# Installation
* pip install -r requirements.txt

# Prerequisite
* `./create_schema.sh`

# Run
* modify conf.json according to your development settings
  * `cp conf.json.example conf.json`
  * `vi conf.json`
* `cd backend`
* batch script
  * in production mode (to team channel)
    * `env MUSIC_RECOMMENDATION_PROFILE=production ./batch.py`
  * in development mode (to private channel)
    * `./batch.py`
* API
  * in production mode
    * `flask run`
  * in development mode
    * `env FLASK_ENV=development flask run`
  * `curl localhost:5000/recommend` or `curl localhost:5000/recomment/2019`
