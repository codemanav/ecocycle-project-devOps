package com.ecocycle.users;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** Spring Boot application main class. */
@SpringBootApplication
@OpenAPIDefinition(
    info =
        @Info(
            title = "EcoCycle Users Service",
            version = "1.0",
            description = "APIs for managing users in EcoCycle"))
public class UsersServiceApplication {
  public static void main(String[] args) {
    SpringApplication.run(UsersServiceApplication.class, args);
  }
}
