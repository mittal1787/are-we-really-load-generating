// Java Program to Set up a Basic HTTP Server
// Source: https://www.geeksforgeeks.org/how-to-set-up-a-basic-http-server-in-java/
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
 
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
 
// Driver Class
public class SimpleHttpServer 
{
    // Main Method
    public static void main(String[] args) throws IOException 
    {
        // Create an HttpServer instance
        HttpServer server = HttpServer.create(new InetSocketAddress(8001), 0);
 
        // Create a context for a specific path and set the handler
        server.createContext("/", new MyHandler());
 
        // Start the server
        server.setExecutor(null); // Use the default executor
        server.start();
    }
 
    // define a custom HttpHandler
    static class MyHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException 
        {
            // Print UNIX time in nanoseconds
            System.out.println(System.nanoTime());
            // handle the request
            String response = "Simple HTTP response from Java for Experiment 11";
            exchange.sendResponseHeaders(200, response.length());
            OutputStream os = exchange.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }
}