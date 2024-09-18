import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './authentication/Login';
import Homepage from './Homepage';
import PrivateRoute from './authentication/PrivateRoute'; // Import the PrivateRoute component
import './App.css';

function App() {
	return (
		<Router>
			<Routes>
				<Route
					path="/"
					element={<Login />}
				/>

				{/* Protect the /protected route */}
				<Route
					path="/protected"
					element={
						<PrivateRoute>
							<Homepage />
						</PrivateRoute>
					}
				/>
			</Routes>
		</Router>
	);
}

export default App;
