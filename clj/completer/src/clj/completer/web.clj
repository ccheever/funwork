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
        result (take 20 (completer/by-prefix q))]
    (-> (json/generate-string result)
      (response)
      (content-type "application/json"))))

(defn handler [req]
  (if-let [f (case (:uri req)
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

