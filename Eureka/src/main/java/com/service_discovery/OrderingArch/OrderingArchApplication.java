package com.service_discovery.OrderingArch;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@SpringBootApplication
@EnableEurekaServer
public class OrderingArchApplication {

	public static void main(String[] args) {
		SpringApplication.run(OrderingArchApplication.class, args);
	}

}
