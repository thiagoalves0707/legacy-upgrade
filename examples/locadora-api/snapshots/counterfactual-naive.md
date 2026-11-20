# Snapshot comparison

same: 4, diff: 10, missing: 0, error: 0

- **DIFF** `movies-all`

```diff
--- baseline
+++ current
@@ -4,30 +4,30 @@
     "movies": [
       {
         "available": true,
-        "daily_price": 9.9,
+        "daily_price": "9.90",
         "id": 1,
-        "released": "30/08/2002",
+        "released": "Fri, 30 Aug 2002 00:00:00 GMT",
         "title": "Cidade de Deus"
       },
       {
         "available": true,
-        "daily_price": 7.5,
+        "daily_price": "7.50",
         "id": 2,
-        "released": "03/04/1998",
+        "released": "Fri, 03 Apr 1998 00:00:00 GMT",
         "title": "Central do Brasil"
       },
       {
         "available": false,
-        "daily_price": 12.0,
+        "daily_price": "12.00",
         "id": 3,
-        "released": "05/10/2007",
+        "released": "Fri, 05 Oct 2007 00:00:00 GMT",
         "title": "Tropa de Elite"
       },
       {
         "available": true,
-        "daily_price": 8.25,
+        "daily_price": "8.25",
         "id": 4,
-        "released": "10/09/2000",
+        "released": "Sun, 10 Sep 2000 00:00:00 GMT",
         "title": "O Auto da Compadecida"
       }
     ]
```
- **DIFF** `movies-available-yes`

```diff
--- baseline
+++ current
@@ -4,23 +4,23 @@
     "movies": [
       {
         "available": true,
-        "daily_price": 9.9,
+        "daily_price": "9.90",
         "id": 1,
-        "released": "30/08/2002",
+        "released": "Fri, 30 Aug 2002 00:00:00 GMT",
         "title": "Cidade de Deus"
       },
       {
         "available": true,
-        "daily_price": 7.5,
+        "daily_price": "7.50",
         "id": 2,
-        "released": "03/04/1998",
+        "released": "Fri, 03 Apr 1998 00:00:00 GMT",
         "title": "Central do Brasil"
       },
       {
         "available": true,
-        "daily_price": 8.25,
+        "daily_price": "8.25",
         "id": 4,
-        "released": "10/09/2000",
+        "released": "Sun, 10 Sep 2000 00:00:00 GMT",
         "title": "O Auto da Compadecida"
       }
     ]
```
- **DIFF** `movies-available-false`

```diff
--- baseline
+++ current
@@ -4,9 +4,9 @@
     "movies": [
       {
         "available": false,
-        "daily_price": 12.0,
+        "daily_price": "12.00",
         "id": 3,
-        "released": "05/10/2007",
+        "released": "Fri, 05 Oct 2007 00:00:00 GMT",
         "title": "Tropa de Elite"
       }
     ]
```
- **DIFF** `movies-available-invalid`

```diff
--- baseline
+++ current
@@ -1,5 +1,5 @@
 {
-  "body": "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 3.2 Final//EN\">\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>\n",
+  "body": "<!doctype html>\n<html lang=en>\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>\n",
   "body_kind": "text",
   "headers": {
     "content-type": "text/html; charset=utf-8",
```
- **DIFF** `movie-1`

```diff
--- baseline
+++ current
@@ -1,9 +1,9 @@
 {
   "body": {
     "available": true,
-    "daily_price": 9.9,
+    "daily_price": "9.90",
     "id": 1,
-    "released": "30/08/2002",
+    "released": "Fri, 30 Aug 2002 00:00:00 GMT",
     "title": "Cidade de Deus"
   },
   "body_kind": "json",
```
- **DIFF** `rental-json-3-days`

```diff
--- baseline
+++ current
@@ -2,11 +2,11 @@
   "body": {
     "customer": "Ana",
     "days": 3,
-    "due": "18/01/2024",
+    "due": "Thu, 18 Jan 2024 00:00:00 GMT",
     "id": "<ignored>",
     "movie_id": 2,
-    "start": "15/01/2024",
-    "total": 22.5
+    "start": "Mon, 15 Jan 2024 00:00:00 GMT",
+    "total": "22.50"
   },
   "body_kind": "json",
   "headers": {
```
- **DIFF** `rental-json-7-days-discount`

```diff
--- baseline
+++ current
@@ -2,11 +2,11 @@
   "body": {
     "customer": "Bruno",
     "days": 7,
-    "due": "22/01/2024",
+    "due": "Mon, 22 Jan 2024 00:00:00 GMT",
     "id": "<ignored>",
     "movie_id": 4,
-    "start": "15/01/2024",
-    "total": 51.98
+    "start": "Mon, 15 Jan 2024 00:00:00 GMT",
+    "total": "51.98"
   },
   "body_kind": "json",
   "headers": {
```
- **DIFF** `rental-leap-year`

```diff
--- baseline
+++ current
@@ -2,11 +2,11 @@
   "body": {
     "customer": "Cláudia",
     "days": 2,
-    "due": "01/03/2024",
+    "due": "Fri, 01 Mar 2024 00:00:00 GMT",
     "id": "<ignored>",
     "movie_id": 1,
-    "start": "28/02/2024",
-    "total": 19.8
+    "start": "Wed, 28 Feb 2024 00:00:00 GMT",
+    "total": "19.80"
   },
   "body_kind": "json",
   "headers": {
```
- **DIFF** `rental-form-encoded`

```diff
--- baseline
+++ current
@@ -1,17 +1,9 @@
 {
-  "body": {
-    "customer": "Caio",
-    "days": 2,
-    "due": "17/01/2024",
-    "id": "<ignored>",
-    "movie_id": 1,
-    "start": "15/01/2024",
-    "total": 19.8
-  },
-  "body_kind": "json",
+  "body": "<!doctype html>\n<html lang=en>\n<title>415 Unsupported Media Type</title>\n<h1>Unsupported Media Type</h1>\n<p>Did not attempt to load JSON data because the request Content-Type was not &#39;application/json&#39;.</p>\n",
+  "body_kind": "text",
   "headers": {
-    "content-type": "application/json",
+    "content-type": "text/html; charset=utf-8",
     "location": null
   },
-  "status": 201
+  "status": 415
 }
```
- **DIFF** `rental-malformed-json`

```diff
--- baseline
+++ current
@@ -1,5 +1,5 @@
 {
-  "body": "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 3.2 Final//EN\">\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>The browser (or proxy) sent a request that this server could not understand.</p>\n",
+  "body": "<!doctype html>\n<html lang=en>\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>The browser (or proxy) sent a request that this server could not understand.</p>\n",
   "body_kind": "text",
   "headers": {
     "content-type": "text/html; charset=utf-8",
```
