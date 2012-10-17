(defproject completer "0.1.0-SNAPSHOT"
  :src-paths ["src/clj"]
  :java-source-paths ["src/java"]
  :dependencies [[org.clojure/clojure "1.4.0"]
                 [clj-json "0.5.1"]
                 [ring "1.1.6"]
                 [hiccup "1.0.1"]]
  :jvm-opts ["-server" "-Xmx1G"])
