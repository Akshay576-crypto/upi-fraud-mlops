import {
  useState,
} from "react";

import Home from "./Home";
import Dashboard from "./Dashboard";
import Payment from "./Payment";

import "./App.css";


function App() {

  const [page, setPage] =
    useState("home");


  return (

    <div>

      <nav className="navbar">

        <button
          className="brand"
          onClick={() =>
            setPage("home")
          }
        >
          FRAUD<span>OPS</span>
        </button>


        <div className="nav-links">

          <button
            className={
              page === "home"
                ? "active"
                : ""
            }
            onClick={() =>
              setPage("home")
            }
          >
            Overview
          </button>

          <button
            className={
              page === "dashboard"
                ? "active"
                : ""
            }
            onClick={() =>
              setPage("dashboard")
            }
          >
            Dashboard
          </button>

          <button
            className={
              page === "payment"
                ? "active"
                : ""
            }
            onClick={() =>
              setPage("payment")
            }
          >
            Simulator
          </button>

        </div>

      </nav>


      {page === "home" && (
        <Home
          onNavigate={setPage}
        />
      )}

      {page === "dashboard" && (
        <Dashboard />
      )}

      {page === "payment" && (
        <Payment />
      )}

    </div>
  );
}


export default App;