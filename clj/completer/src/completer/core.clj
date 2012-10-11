(ns completer.core
  (:use (ring.middleware reload
                         stacktrace))
  (:require [clj-json.core :as json]
            [ring.adapter.jetty :as jetty]))


(set! *warn-on-reflection* true)

(defonce data*
  (json/parse-string (slurp "../../shareable_medication.json")
                     true))

;-------------------------------------------------------------------------------

(defn match? [^String s r]
  (some (fn [^String x] (.startsWith x s))
        (map (fn [^String x] (.toLowerCase x))
             (filter string? (vals r)))))

(defn match [^String s]
  (let [s (.toLowerCase s)]
    (doall
      (remove nil?
              (map (fn [r] (if (match? s r) r nil)) data*)))))

;-------------------------------------------------------------------------------

(defn str-prefixes [^String s]
  (for [i (range 1 (inc (.length s)))]
    (.substring s 0 i)))

(defn tokens [r]
  (flatten
    (map (fn [^String x] (into [] (.split x "[^a-z0-9]")))
         (map (fn [^String x] (.toLowerCase x))
              (filter string?
                      (vals r))))))

(defn prefixes [r]
  (set
    (flatten
      (apply concat (map str-prefixes (tokens r))))))

(defn conjmerge [lis]
  (apply (partial merge-with conj) lis))

(defn prefix-index []
  (conjmerge
    (for [r data*]
      (conjmerge
        (for [p (prefixes r)]
          {p #{r}})))))

(defonce pindex* (prefix-index))

;-------------------------------------------------------------------------------
; webserver
;-------------------------------------------------------------------------------

(defn handler [req]
  {:status 200
   :body "hello world"})

(def app
  (-> #'handler
    (wrap-reload)
    (wrap-stacktrace)))

(defn -main [& args]
  (jetty/run-jetty #'app {:port 8080 :join? false}))


