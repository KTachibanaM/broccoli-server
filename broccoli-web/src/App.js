import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link, Switch, Redirect } from "react-router-dom"
import Icon from "./icon.png"
import ContentClient from "./clients/ContentClient"

import ViewWorkersPage from "./pages/workers/ViewWorkersPage"
import CreateWorkerPage from "./pages/workers/CreateWorkerPage"
import ViewBoardsPage from "./pages/content/ViewBoardsPage"
import UpsertBoardPage from "./pages/content/UpsertBoardPage"
import Board from "./pages/content/Board"
import Worker from "./pages/workers/Worker"

import applyMessage from "./hoc/applyMessage"
import applyRouting from "./hoc/applyRouting"
import applyApiAuth from "./hoc/applyApiAuth"
import applyWorkerManagerAuth from "./hoc/applyWorkerManagerAuth"

export default class App extends Component {
  constructor(props) {
    super(props);
    this.contentClient = new ContentClient(
      process.env.REACT_APP_SERVER_HOSTNAME,
      parseInt(process.env.REACT_APP_SERVER_PORT)
    );
  }

  render() {
    return (
      <Router>
        <div>
          <div>
            <img src={Icon} alt="Broccoli logo" height="16" width="16"/>
            { ' Broccoli' }
            { ' | ' }
            <Link to="/boards/view">View boards</Link>
            { ' | ' }
            <Link to="/boards/upsert">Create new board</Link>
            { ' | ' }
            <Link to="/workers/view">View workers</Link>
            { ' | ' }
            <Link to="/workers/create">Create new worker</Link>
          </div>
          <Switch>
            <Redirect
              exact
              from="/"
              to="/boards/view"
            />
            <Route
              exact
              path="/boards/view"
              component={() => {
                const EnhancedPage = applyHoc(ViewBoardsPage, applyMessage, applyRouting, applyApiAuth);
                return (<EnhancedPage />)
              }}
            />
            <Route
              exact
              path="/boards/upsert"
              component={() => {
                const EnhancedPage = applyHoc(UpsertBoardPage, applyMessage, applyRouting, applyApiAuth);
                return (<EnhancedPage />)
              }}
            />
            <Route
              exact
              path="/board/:name"
              component={() => {
                const EnhancedPage = applyHoc(Board, applyMessage, applyApiAuth);
                return (<EnhancedPage
                  contentClient={this.contentClient}
                />)
              }}
            />
            <Route
              exact
              path="/workers/view"
              component={() => {
                const EnhancedPage = applyHoc(ViewWorkersPage, applyMessage, applyRouting, applyWorkerManagerAuth);
                return (<EnhancedPage />)
              }}
            />
            <Route
              exact
              path="/workers/create"
              component={() => {
                const EnhancedPage = applyHoc(CreateWorkerPage, applyMessage, applyRouting, applyWorkerManagerAuth);
                return (<EnhancedPage />)
              }}
            />
            <Route
              exact
              path="/worker/:workerId"
              component={() => {
                const EnhancedPage = applyHoc(Worker, applyMessage, applyWorkerManagerAuth);
                return (<EnhancedPage />)
              }}
            />
          </Switch>
        </div>
      </Router>
    );
  }
}

function applyHoc(Component, ...hocList) {
  for (let hoc of hocList) {
    Component = hoc(Component)
  }
  return Component
}
