import React, {Component} from 'react';
import 'semantic-ui-css/semantic.min.css';
import {Container, Menu} from 'semantic-ui-react'
import { BrowserRouter as Router, Route, Link, Switch, Redirect } from "react-router-dom"
import StreamPage from "./StreamPage"
import RandomPage from "./RandomPage"
import ApiClient from './ApiClient'

class App extends Component {
  constructor(props) {
    super(props);
    this.apiClient = new ApiClient(
      process.env.REACT_APP_API_HOSTNAME,
      parseInt(process.env.REACT_APP_API_PORT),
      process.env.REACT_APP_S3_HOSTNAME,
      parseInt(process.env.REACT_APP_S3_PORT),
      process.env.REACT_APP_S3_BUCKET_NAME
    );
  }

  render() {
    return (
      <Router>
        <Container>
          <Menu inverted>
            <Menu.Item header>Herr あし</Menu.Item>
            <Link to="/stream">
              <Menu.Item name='Stream'/>
            </Link>
            <Link to="/random">
              <Menu.Item name='Random'/>
            </Link>
          </Menu>
          <Switch>
            <Redirect
              exact
              from="/"
              to="/stream"
            />
            <Route
              exact
              path="/stream"
              component={() => {
                return (<StreamPage apiClient={this.apiClient} columnCount={3}/>)
              }}
            />
            <Route
              exact
              path="/random"
              component={() => {
                return (<RandomPage apiClient={this.apiClient} columnCount={3}/>)
              }}
            />
          </Switch>
        </Container>
      </Router>
    );
  }
}

export default App;
