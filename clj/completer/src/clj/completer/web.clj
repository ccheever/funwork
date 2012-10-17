(ns completer.web
  (:use (ring.middleware reload
                         params
                         stacktrace)
        ring.util.response)
  (:require [completer.completer :as completer]
            [ring.adapter.jetty :as jetty]
            [clj-json.core :as json]))

(defn render-search [req]
  (let [q (get-in req [:params "q"])
        ids (take 20 (completer/by-prefix q))
        result (map completer/by-id ids)]
    (-> (json/generate-string result)
      (response)
      (content-type "application/json"))))

(defn render-index [req]
  (-> (slurp "../../index.html")
    (response)
    (content-type "text/html")))

(defn render-index-js [req]
  (-> (slurp "../../index.js")
    (response)
    (content-type "text/javascript")))

(defn render-index-css [req]
  (-> (slurp "../../index.css")
    (response)
    (content-type "text/css")))

(defn handler [req]
  (if-let [f (case (:uri req)
               "/" render-index
               "/index.js" render-index-js
               "/index.css" render-index-css
               "/search" render-search
               (fn [req] (not-found
                           (str "404 path not found: " (:uri req)))))]
    (f req)))

(def app
  (-> #'handler
    (wrap-params)
    (wrap-reload)
    (wrap-stacktrace)))

(defn -main [& args]
  (jetty/run-jetty #'app {:port 8080 :join? false}))

