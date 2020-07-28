import React, { Component } from 'react';
import { Route, Link, Switch, Redirect } from "react-router-dom"
import Icon from "./icon.png"

import ViewWorkersPage from "./pages/workers/ViewWorkersPage"
import CreateWorkerPage from "./pages/workers/CreateWorkerPage"
import ViewBoardsPage from "./pages/modView/ViewBoardsPage"
import Board from "./pages/modView/Board"
import Worker from "./pages/workers/Worker"
import ApiClient from "./api/ApiClient";

import withMessage from "./hoc/withMessage"
import withRouting from "./hoc/withRouting"
import withAuth from "./hoc/withAuth"

function applyHoc(Component, ...hocList) {
  for (let hoc of hocList) {
    Component = hoc(Component)
  }
  return Component
}

export default class App extends Component {
  constructor(props) {
    super(props);
    this.apiClient = new ApiClient()
    this.state = {
      threadCount: -1
    }
  }

  componentDidMount() {
    this.apiClient.getThreadCount()
      .then(threadCount => {
        this.setState({ threadCount })
      })
  }

  render() {
    return (
      <div>
        <div>
          <img src={Icon} alt="Broccoli logo" height="16" width="16"/>
          { ' Broccoli' }
          { ' | ' }
          <Link to="/boards/view">Mod views</Link>
          { ' | ' }
          <Link to="/workers/view">Workers</Link>
          { ' | ' }
          <Link to="/workers/create">Create new worker</Link>
          { ' | ' }
          <Link to="/oneOffJobs/view">One off jobs</Link>
          { ' | ' }
          { `Thread count: ${this.state.threadCount}` }
          { ' | ' }
          <button onClick={e => {
            e.preventDefault()
            this.apiClient.unsetAuth();
          }}>Logout</button>
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
              const EnhancedPage = applyHoc(ViewBoardsPage, withMessage, withRouting, withAuth);
              return (<EnhancedPage />)
            }}
          />
          <Route
            exact
            path="/board/:name"
            component={() => {
              const EnhancedPage = applyHoc(Board, withMessage, withAuth);
              return (<EnhancedPage />)
            }}
          />
          <Route
            exact
            path="/workers/view"
            component={() => {
              const EnhancedPage = applyHoc(ViewWorkersPage, withMessage, withRouting, withAuth);
              return (<EnhancedPage />)
            }}
          />
          <Route
            exact
            path="/workers/create"
            component={() => {
              const EnhancedPage = applyHoc(CreateWorkerPage, withMessage, withRouting, withAuth);
              return (<EnhancedPage />)
            }}
          />
          <Route
            exact
            path="/worker/:workerId"
            component={() => {
              const EnhancedPage = applyHoc(Worker, withMessage, withAuth);
              return (<EnhancedPage />)
            }}
          />
        </Switch>
      </div>
    );
  }
}
