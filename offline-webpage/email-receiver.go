package main

import (
	"log"
	"net/http"
	"strings"
	"time"

	"database/sql"

	_ "github.com/mattn/go-sqlite3"
)

func main() {

	db, err := sql.Open("sqlite3", "./emails-to-notify.sqlite")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// sqlStmt := `
	// create table emails (id integer primary key, email text not null unique, ip text not null, date integer not null);
	// `
	// _, err = db.Exec(sqlStmt)
	// if err != nil {
	// 	log.Fatal(err)
	// }

	http.HandleFunc("/", page(db))

	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal(err)
	}
}

func errorCodeHandler(code int) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, http.StatusText(code), code)
	}
}

func page(db *sql.DB) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {

		case http.MethodGet:
			http.ServeFile(w, r, "./index.html")

		case http.MethodPost:

			email := r.FormValue("email-to-notify")
			if email == "" {
				log.Printf("error: email not found in request\n")
				errorCodeHandler(http.StatusBadRequest)(w, r)
				return
			}

			socket := strings.Split(r.RemoteAddr, ":")
			if len(socket) != 2 {
				log.Printf("error while parsing client IP %v\n", socket)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			ip := socket[0]
			now := time.Now().Unix()
			delay := int64(30)
			max := 2

			stmt, err := db.Prepare("select count(*) from emails where ip = ? and date >= ?")
			if err != nil {
				log.Printf("error: %v while preparing query %v\n", err, stmt)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			defer stmt.Close()
			rows, err := stmt.Query(ip, now-delay)
			if err != nil {
				log.Printf("error: %v while executing query %v\n", err, stmt)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			if !rows.Next() {
				log.Printf("error while retrieving the count of email addresses inserted from IP %v\n", ip)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			n := 0
			err = rows.Scan(&n)
			if err != nil {
				log.Printf("error: %v parsing the count of email addresses inserted from IP %v\n", err, ip)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			if rows.Close() != nil {
				log.Printf("error closing rows after parsing the count of email addresses inserted from IP %v\n", ip)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			log.Printf("%v emails already stored for IP %v during the last %v seconds\n", n, ip, delay)

			if n >= max {
				log.Printf("too many email addresses submitted by IP %v during the last %v seconds\n", ip, delay)
				errorCodeHandler(http.StatusForbidden)(w, r)
				return
			}

			stmt, err = db.Prepare("insert into emails(email, ip, date) values(?, ?, ?)")
			if err != nil {
				log.Printf("error: %v while preparing query %v\n", err, stmt)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}
			defer stmt.Close()
			_, err = stmt.Exec(email, ip, now)
			if err != nil {
				log.Printf("error: %v while executing query %v\n", err, stmt)
				errorCodeHandler(http.StatusInternalServerError)(w, r)
				return
			}

			log.Printf("record inserted: (email: %v, ip: %v, date: %v)\n", email, ip, now)
			http.ServeFile(w, r, "./index.html")

		default:
		}
	}
}
