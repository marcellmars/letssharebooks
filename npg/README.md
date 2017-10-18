# Dev notes
## Getting started with development

  * docker run -d -p 27017:27017 mongo
    * clean up docker clutter:
    `docker rmi $(docker images -a -q)`
    `docker rm $(docker ps -a -q)`
    `docker volume rm $(docker volume ls -f dangling=true -q)`
    
  * rest-backend/
    * python3 run.py
    
## Development Vue

  * `$ vue init webpack vue-frontend` 
 > output:
 
<pre>
? Project name vue-frontend
? Project description Memory of the World
? Author 
? Vue build standalone
? Install vue-router? Yes
? Use ESLint to lint your code? Yes
? Pick an ESLint preset Standard
? Setup unit tests with Karma + Mocha? No
? Setup e2e tests with Nightwatch? No

   vue-cli · Generated "vue-frontend".

   To get started:
   
     cd vue-frontend
     npm install
     npm run dev

 **check package.json for dependencies**

## Mongodb notes
> this will sort ngrams with largest number of candidates/authors:
 * db.authors_ngrams.aggregate([{$project: {count: {$size:"$authors"}}}, {$sort: {'count':-1}}])
