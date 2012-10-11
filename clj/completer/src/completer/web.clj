(ns completer.web
  (:use (ring.middleware reload
                         stacktrace)
        ring.util.response)
  (:require [ring.adapter.jetty :as jetty]
            [clj-json.core :as json]))


(defn render-search [req]
  (let [q (get-in req [:params "q"])
        result (pindex* q)]
    (-> (json/generate-string result)
      (response)
      (content-type "application/json"))))

(defn handler [req]
  (if-let [f (case (:uri req)
               "/search" render-search)]
    (f req)
    (not-found)))

(def app
  (-> #'handler
    (wrap-reload)
    (wrap-stacktrace)))

(defn -main [& args]
  (jetty/run-jetty #'app {:port 8080 :join? false}))

