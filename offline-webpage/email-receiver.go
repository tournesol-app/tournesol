package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/", page)

	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal(err)
	}
}

func page(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		http.ServeFile(w, r, "./index.html")
	case http.MethodPost:
		fmt.Println(r.FormValue("email-to-notify"))
		http.ServeFile(w, r, "./index.html")
	default:
	}
}
