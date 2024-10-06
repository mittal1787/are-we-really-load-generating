package main

import (
    "fmt"
    "log"
	"os"
    "net/http"
	"time"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/", handler)

    server := &http.Server{
        Addr:    ":8000",
        Handler: mux,
    }

    err := server.ListenAndServeTLS("server.crt", "server.key")
    if err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
}

func handler(w http.ResponseWriter, r *http.Request) {
	duration, err := time.ParseDuration(os.Args[1])
	fmt.Println(time.Now().UnixNano())
	if err == nil {
		time.Sleep(duration)
	} 
	fmt.Fprintf(w, "HTTP Version: %s\n", r.Proto)
}