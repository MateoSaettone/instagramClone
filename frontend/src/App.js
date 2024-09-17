// import "./App.css";
// import Authentication from "./authentication/Authentication";
// import Homepage from "./Homepage";

// //"yrn start" on terminal to run

// function App() {
// 	return (
// 		<div className="app">
// 			{/*<Homepage />*/}
// 			<Authentication />
// 		</div>
// 	);
// }

// export default App;

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './authentication/Login';
import Homepage from "./Homepage";
import "./App.css";

function App() {
	return (
		<Router>
			<Routes>
				<Route
					path="/"
					element={<Login />}
				/>
				<Route
					path="/protected"
					element={<Homepage />}
				/>
			</Routes>
		</Router>
	);
}

export default App;
