package main

import (
	"fmt"
	"net/http"
	"os"
	"time"
)

const (
	delta       = 100 * time.Millisecond
	duration    = time.Minute
	serverPort  = 8080
	workerCount = 100
)

func main() {
	// define flag channel
	start := make(chan bool)
	stop := make(chan bool)

	// spawn a bunch of workers
	for i := 0; i < workerCount; i++ {
		go worker(start, stop)
	}

	// send start signal
	close(start)

	// wait for the workers to work
	<-time.After(duration)

	// send signal to stop
	close(stop)
}

func worker(start chan bool, stop chan bool) {
	// signal to start working
	<-start

	for {
		select {
		case <-time.After(delta):
			go sendRequest()
		case <-stop:
			return
		}
	}
}

func sendRequest() {
	requestURL := fmt.Sprintf("http://localhost:%d", serverPort)
	res, err := http.Get(requestURL)
	if err != nil {
		fmt.Printf("error making http request: %s\n", err)
		os.Exit(1)
	}
	fmt.Print(res)
}
