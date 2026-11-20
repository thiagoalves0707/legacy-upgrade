# Snapshot comparison

same: 11, diff: 2, missing: 0, error: 0

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
+  "body": "<!doctype html>\n<html lang=en>\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>The browser (or proxy) sent a request that this server could not understand.</p>\n",
+  "body_kind": "text",
   "headers": {
-    "content-type": "application/json",
+    "content-type": "text/html; charset=utf-8",
     "location": null
   },
-  "status": 201
+  "status": 400
 }
```
