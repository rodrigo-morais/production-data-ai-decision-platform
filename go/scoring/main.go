package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"time"
)

type request struct {
	Impact   float64 `json:"impact"`
	Urgency  float64 `json:"urgency"`
	Coverage float64 `json:"coverage"`
}

type response struct {
	Score float64 `json:"score"`
}

func clamp(value float64) float64 {
	if value < 0 {
		return 0
	}
	if value > 1 {
		return 1
	}
	return value
}

func score(input request) float64 {
	return clamp(0.45*input.Impact + 0.35*input.Urgency + 0.20*input.Coverage)
}

func scoreHandler(writer http.ResponseWriter, req *http.Request) {
	if req.Method != http.MethodPost {
		http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	decoder := json.NewDecoder(http.MaxBytesReader(writer, req.Body, 1<<20))
	decoder.DisallowUnknownFields()
	var input request
	if err := decoder.Decode(&input); err != nil {
		http.Error(writer, "invalid request", http.StatusBadRequest)
		return
	}
	writer.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(writer).Encode(response{Score: score(input)})
}

func main() {
	healthcheck := flag.Bool("healthcheck", false, "check the local health endpoint")
	flag.Parse()
	if *healthcheck {
		client := http.Client{Timeout: time.Second}
		response, err := client.Get("http://localhost:8081/health")
		if err != nil || response.StatusCode != http.StatusOK {
			os.Exit(1)
		}
		return
	}

	http.HandleFunc("/health", func(writer http.ResponseWriter, _ *http.Request) {
		writer.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprint(writer, `{"status":"ok"}`)
	})
	http.HandleFunc("/score", scoreHandler)
	if err := http.ListenAndServe(":8081", nil); err != nil {
		panic(err)
	}
}
