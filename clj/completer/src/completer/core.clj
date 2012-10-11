(ns completer.core
  (:use (ring.middleware reload
                         stacktrace))
  (:require [clj-json.core :as json]
            [ring.adapter.jetty :as jetty]
            [taoensso.nippy :as nippy]))

;-------------------------------------------------------------------------------

(set! *warn-on-reflection* true)

(defn nip-freeze [data ^String file]
  (with-open [fos (java.io.FileOutputStream. file)
              dos (java.io.DataOutputStream. fos)]
    (nippy/freeze-to-stream! dos data)))

(defn freeze [data ^String file]
  (with-open [fos (java.io.FileOutputStream. file)
              oos (java.io.ObjectOutputStream. fos)]
    (.writeObject oos data)))

;-------------------------------------------------------------------------------

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
  (into #{}
        (for [t (tokens r)
              p (str-prefixes t)]
          p)))

(defn prefix-index []
  (apply (partial merge-with clojure.set/union)
    (for [r data*
          p (prefixes r)]
      {p #{r}})))

;(defonce pindex* (time (prefix-index)))

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


