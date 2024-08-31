package main

import (
	"flag"
	"time"
	"fmt"
	"log"
	"net/http"
	"strconv"
)

func main() {
	wwwPort := flag.Int("port", 8001, "http port")

	flag.Parse()

	http.HandleFunc("/", handler)

	log.Printf("Starting HTTP server on port %d", *wwwPort)
	err := http.ListenAndServe(":"+strconv.Itoa(*wwwPort), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(time.Now().UnixNano())
	prod := 1
	for i := 1; i < 100000; i++ {
		for j := 1; j < 100000; j++ {
			prod *= i*j
		}
	}
	fmt.Fprint(w, prod)
}
