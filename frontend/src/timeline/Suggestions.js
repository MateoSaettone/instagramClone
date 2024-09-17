import { Avatar } from "@mui/material";
import React from "react";
import "./Suggestions.css";

function Suggestions({ user =  "404"}) {
  return (
    <div className="suggestions">
      <div className="suggestions__title">Suggestions for you</div>
      <div className="suggestions__usernames">
        <div className="suggestions__username">
          <div className="username__left">
            <span className="avatar">
              <Avatar>{user.charAt(0).toUpperCase()}</Avatar>
            </span>
            <div className="username__info">
              <span className="username">{user}</span>
              <span className="relation">New to Instagram</span>
            </div>
          </div>
          <button className="follow__button">Follow</button>
        </div>
      </div>
    </div>
  );
}

export default Suggestions;