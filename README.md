# Microservices_ServiceDiscovery
This repository is a project demonstrating a Python-based microservice architecture with Docker containerization and service discovery integration, featuring comparisons between Eureka, Consul, and Amalgam8.

### What is Microservice Basically?
Microservices are an architectural style where an application is built as a collection of small, independent services. Each service focuses on a single business function and communicates with other services through lightweight protocols, typically HTTP or messaging queues. This approach improves scalability, flexibility, and ease of maintenance.

### What is Service Discovery Basically?
Service Discovery is the process by which services in a distributed system automatically detect each other's network locations (IP and port). As services scale, restart, or move, service discovery ensures that communication stays reliable without manual configuration.

### What is Containerization Basically?
Containerization is a method of packaging an application along with its dependencies, configurations, and runtime environment into a single portable unit called a container. Containers ensure that the application runs the same way regardless of where it is deployed, improving consistency and efficiency.

### Why Do We Use Docker?
Docker simplifies application deployment by allowing developers to package applications and their environments into containers. This makes development, testing, and deployment faster and more predictable, while also enabling better resource isolation and scalability across different systems. <b><i>Podman, CRI-O, containerd</b></i> are also some of the examples for containerization programs.

### Shortly Information about Eureka, Consul and Amalgam8:
<b>Eureka:</b> A service registry developed by Netflix, designed for locating services in cloud-based systems. It helps microservices find and communicate with each other dynamically.

<b>Consul:</b> A tool by HashiCorp that provides service discovery, health checking, and key-value storage. It is widely used for both service registration and distributed configuration.

<b>Amalgam8:</b> An open-source service mesh developed by IBM for microservices. It provides service discovery, traffic routing, and fault tolerance for cloud-native applications.

<br>

<table>
  <tr>
    <th>Concept </th>
    <th>What It Does? </th>
    <th>Real Life Analogy</th>
  </tr>
  <tr>
    <th>Image </th>
    <th>Blueprint of your app & environment </th>
    <th>Game installer (.exe)</th>
  </tr><tr>
    <th>Container </th>
    <th>Running instance of an image </th>
    <th>Open game window (running game)</th>
  </tr>
  <tr>
    <th>Microservice </th>
    <th>Self-contained business logic (small app) </th>
    <th>Log-in client for a online game</th>
  </tr><tr>
    <th>Service Discovery </th>
    <th>Finds other services dynamically via a registry </th>
    <th>Address Book for services</th>
  </tr>
</table>
