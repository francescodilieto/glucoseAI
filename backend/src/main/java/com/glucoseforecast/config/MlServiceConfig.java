package com.glucoseforecast.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.net.http.HttpClient;

@Configuration
public class MlServiceConfig {

    @Bean
    public RestClient mlServiceRestClient(@Value("${ml-service.base-url}") String baseUrl) {
        // Force HTTP/1.1: the JDK client's HTTP/2 upgrade negotiation confuses
        // uvicorn (h11), which then fails to parse the request body.
        HttpClient httpClient = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        return RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(new JdkClientHttpRequestFactory(httpClient))
                .build();
    }
}
