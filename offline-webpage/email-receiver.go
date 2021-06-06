package main

import (
	"fmt"
	"log"
	"net/http"
	"net"
	"time"

	"database/sql"

	_ "github.com/mattn/go-sqlite3"
)

type config struct {
	dbFile                   string
	address                  string
	port                     int
	pageFile                 string
	emailFormKey             string
	throttlingDelay          int64
	throttlingMaxSubmissions int
}

type server struct {
	*config
	*sql.DB
}

func (s *server) openDB() error {
	db, err := sql.Open("sqlite3", s.config.dbFile)
	if err != nil {
		return err
	}
	s.DB = db
	return nil
}

func main() {
	config := &config{
		dbFile:                   "./emails-to-notify.sqlite",
		address:                  "127.0.0.1",
		port:                     8080,
		pageFile:                 "./index.html",
		emailFormKey:             "email-to-notify",
		throttlingDelay:          60*60*24, // 1 day
		throttlingMaxSubmissions: 10,
	}

	s := &server{
		config: config,
	}
	if err := s.openDB(); err != nil {
		log.Fatal(err)
	}
	defer s.DB.Close()

	http.HandleFunc("/", s.handle)

	if err := http.ListenAndServe(fmt.Sprintf("%v:%v", config.address, config.port), nil); err != nil {
		log.Fatal(err)
	}
}

func (s *server) handle(w http.ResponseWriter, r *http.Request) {
	switch r.Method {

	case http.MethodGet:
		http.ServeFile(w, r, s.pageFile)

	case http.MethodPost:

		email := r.FormValue(s.emailFormKey)
		if email == "" {
			log.Printf("error: email not found in request\n")
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		ip := r.Header.Get("X-Forwarded-For")
		if ip == "" {
			directIP, _, err := net.SplitHostPort(r.RemoteAddr)
			if err != nil {
				log.Printf("error while parsing client IP %v\n", r.RemoteAddr)
				http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
				return
			}
			ip = directIP
		}

		now := time.Now().Unix()

		query := "select count(*) from emails where ip = ? and date >= ?"
		stmt, err := s.Prepare(query)
		if err != nil {
			log.Printf("error: %v while preparing query %v\n", err, query)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		defer stmt.Close()
		rows, err := stmt.Query(ip, now-s.throttlingDelay)
		if err != nil {
			log.Printf("error: %v while executing query %v\n", err, stmt)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		if !rows.Next() {
			log.Printf("error while retrieving the count of email addresses inserted from IP %v during the last %v seconds\n", ip, s.throttlingDelay)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		n := 0
		if err := rows.Scan(&n); err != nil {
			log.Printf("error: %v parsing the count of email addresses inserted from IP %v during the last %v seconds\n", err, ip, s.throttlingDelay)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		if rows.Close() != nil {
			log.Printf("error closing rows after parsing the count of email addresses inserted from IP %v during the last %v seconds\n", ip, s.throttlingDelay)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		log.Printf("%v emails already stored for IP %v during the last %v seconds\n", n, ip, s.throttlingDelay)

		if n >= s.throttlingMaxSubmissions {
			log.Printf("too many email addresses submitted by IP %v during the last %v seconds\n", ip, s.throttlingDelay)
			http.Error(w, "too many email addresses submitted, try again later", http.StatusForbidden)
			return
		}

		query = "select count(*) from emails where email = ?"
		stmt, err = s.Prepare(query)
		if err != nil {
			log.Printf("error: %v while preparing query %v\n", err, query)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		defer stmt.Close()
		rows, err = stmt.Query(email)
		if err != nil {
			log.Printf("error: %v while executing query %v\n", err, stmt)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		if !rows.Next() {
			log.Printf("error while checking if email address %v is already stored\n", email)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		n = 0
		if err := rows.Scan(&n); err != nil {
			log.Printf("error: %v parsing the count of email address %v appearances\n", err, email)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		if rows.Close() != nil {
			log.Printf("error closing rows after parsing the count of email address %v appearances\n", email)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		if n > 0 {
			log.Printf("email address %v already stored\n", email)
			http.Error(w, "email address already registered", http.StatusBadRequest)
			return
		}

		query = "insert into emails(email, ip, date) values(?, ?, ?)"
		stmt, err = s.Prepare(query)
		if err != nil {
			log.Printf("error: %v while preparing query %v\n", err, query)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		defer stmt.Close()
		_, err = stmt.Exec(email, ip, now)
		if err != nil {
			log.Printf("error: %v while executing query %v\n", err, stmt)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		log.Printf("record inserted: (email: %v, ip: %v, date: %v)\n", email, ip, now)
		http.ServeFile(w, r, s.pageFile)

	default:
		log.Printf("error: unhandled HTTP method")
		http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		return
	}
}
