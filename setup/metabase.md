# Install Metabase

- Download the Metabase [**JAR file**](https://www.metabase.com/start/oss/) (or your method of choice, JAR file was used as Metabase through Docker wasn't working on M1 Macs at the time of this writing)
- Create a new directory and move the Metabase JAR file into it
- Ensure the [**latest Java version**](https://www.oracle.com/java/technologies/downloads/#jdk19-mac) is downloaded
- cd into the new Metabase directory and run the JAR
  ```
  java -jar metabase.jar
  ```
- Metabase is now available on http://localhost:3000/setup
- Set up the connection and use host: localhost
