def build_prompt(stack):
    if stack == "python":
        return """
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "app.py"]
""".strip()

    if stack == "node":
        return """
FROM node:18-alpine
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
CMD ["node", "index.js"]
""".strip()

    if stack == "java":
        return """
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline

COPY . .
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
CMD ["java", "-jar", "app.jar"]
""".strip()

    return ""


