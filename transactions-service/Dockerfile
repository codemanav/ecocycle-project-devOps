# Multi-stage build for transactions-service
# Stage 1: Build the application
FROM maven:3.9.6-eclipse-temurin-17 AS builder


WORKDIR /app

# Copy Maven wrapper and pom.xml first for better layer caching
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies (this layer will be cached if pom.xml doesn't change)
RUN mvn dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application (skip tests in Docker build, they run in CI)
RUN mvn clean package -DskipTests -Dcheckstyle.skip=true -Dspotless.check.skip=true -B

# Stage 2: Create the runtime image
FROM eclipse-temurin:17-jre-jammy

# Add metadata
LABEL maintainer="mdshah5@ncsu.edu"
LABEL service="transactions-service"
LABEL version="1.0.0"

# Create non-root user for security
RUN groupadd -r ecocycle && useradd -r -g ecocycle ecocycle

WORKDIR /app

# Copy the built JAR from builder stage
COPY --from=builder /app/target/*.jar app.jar

# Change ownership to non-root user
RUN chown -R ecocycle:ecocycle /app

# Switch to non-root user
USER ecocycle

# Expose the application port
EXPOSE 8082

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8082/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", \
    "-XX:+UseContainerSupport", \
    "-XX:MaxRAMPercentage=75.0", \
    "-Djava.security.egd=file:/dev/./urandom", \
    "-jar", \
    "app.jar"]

