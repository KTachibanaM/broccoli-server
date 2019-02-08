import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link, Switch, Redirect } from "react-router-dom"
import Icon from "./icon.png"
import WorkerManagerClient from "./clients/WorkerManagerClient"
import ContentClient from "./clients/ContentClient"
import BoardsConfigStore from "./clients/BoardsConfigStore"
import ApiClient from "./clients/ApiClient"

import ViewWorkersPage from "./pages/workers/ViewWorkersPage"
import CreateWorkerPage from "./pages/workers/CreateWorkerPage"
import ViewBoardsPage from "./pages/content/ViewBoardsPage"
import UpsertBoardPage from "./pages/content/UpsertBoardPage"
import Board from "./pages/content/Board"
import ApiPage from "./pages/ApiPage"

import applyMessage from "./hoc/applyMessage"
import applyRouting from "./hoc/applyRouting"

export default class App extends Component {
  constructor(props) {
    super(props);
    // todo: make it config
    this.workerManagerClient = new WorkerManagerClient("localhost", 5002);
    // todo: make it config
    this.contentClient = new ContentClient("localhost", 5000);
    this.boardsConfigStore = new BoardsConfigStore();
    // todo: make it config
    this.apiClient = new ApiClient("localhost", 5001)
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
            <Link to="/api">Configure API</Link>
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
                const EnhancedPage = applyHoc(ViewBoardsPage, applyRouting);
                return (<EnhancedPage boardsConfigStore={this.boardsConfigStore}/>)
              }}
            />
            <Route
              exact
              path="/boards/upsert"
              component={() => {
                const EnhancedPage = applyHoc(UpsertBoardPage, applyMessage, applyRouting);
                return (<EnhancedPage boardsConfigStore={this.boardsConfigStore}/>)
              }}
            />
            <Route
              exact
              path="/board/:name"
              component={() => {
                const EnhancedPage = applyHoc(Board, applyMessage);
                return (<EnhancedPage
                  contentClient={this.contentClient}
                  boardsConfigStore={this.boardsConfigStore}
                />)
              }}
            />
            <Route
              exact
              path="/api"
              component={() => {
                const EnhancedPage = applyHoc(ApiPage, applyMessage);
                return (<EnhancedPage apiClient={this.apiClient} />)
              }}
            />
            <Route
              exact
              path="/workers/view"
              component={() => {
                const EnhancedPage = applyHoc(ViewWorkersPage, applyMessage, applyRouting);
                return (<EnhancedPage workerManagerClient={this.workerManagerClient} />)
              }}
            />
            <Route
              exact
              path="/workers/create"
              component={() => {
                const EnhancedPage = applyHoc(CreateWorkerPage, applyMessage, applyRouting);
                return (<EnhancedPage workerManagerClient={this.workerManagerClient} />)
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
