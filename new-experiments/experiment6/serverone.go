package main

import (
	"flag"
	"time"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"os"
	"io"
)

func main() {
	wwwDir := flag.String("www", "www", "directory with files to be served")
	wwwPort := flag.Int("port", 8000, "http port")

	flag.Parse()

	log.Printf("Serving files from '%s'", *wwwDir)

	http.HandleFunc("/", handler)

	log.Printf("Starting HTTP server on port %d", *wwwPort)
	err := http.ListenAndServe(":"+strconv.Itoa(*wwwPort), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(time.Now().UnixNano())
	res, err := http.Get("http://" + os.Args[1] + ":8001")
	if err != nil {
		fmt.Fprint(w, "error")
	} else {
		resBody, err := io.ReadAll(res.Body)
		if err != nil {
			fmt.Fprint(w, "error")
		} else {
			fmt.Fprint(w, string(resBody))
		}
	}
}
