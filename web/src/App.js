import React, { Component } from 'react';
import { Route, Switch, Redirect } from "react-router-dom"
import { MuiThemeProvider, Container, createStyles, withStyles, createMuiTheme } from "@material-ui/core";
import {AppNav} from "@k-t-corp/frontend-lib"

import ViewWorkersPage from "./pages/workers/ViewWorkersPage"
import CreateWorkerPage from "./pages/workers/CreateWorkerPage"
import ViewBoardsPage from "./pages/modView/ViewBoardsPage"
import Board from "./pages/modView/ViewBoard"
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

const styles = (theme) => createStyles({
  main: {
    // top and bottom padding's
    padding: theme.spacing(4, 0, 3),
  }
});

const theme = createMuiTheme({
  palette: {
    primary: {
      light: '#439889',
      main: '#00695c',
      dark: '#003d33',
      contrastText: '#ffffff'
    },
    secondary: {
      light: '#df78ef',
      main: '#ab47bc',
      dark: '#790e8b',
      contrastText: '#ffffff'
    }
  }
});

class App extends Component {
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
    const {classes} = this.props;

    return (
      <MuiThemeProvider theme={theme}>
        <AppNav
          title='Broccoli'
          items={[
            {
              text: 'Mod Views',
              action: () => {
                window.location.replace("/boards/view")
              }
            },
            {
              text: 'Workers',
              action: () => {
                window.location.replace("/workers/view")
              }
            },
            {
              text: 'Create worker',
              action: () => {
                window.location.replace("/workers/create")
              }
            },
            {
              text: 'Jobs',
              action: () => {
                window.location.replace("/oneOffJobs/view")
              }
            },
            {
              text: `Thread count: ${this.state.threadCount}`,
              action: () => {}
            },
          ]}
          rightMostItem={{
            text: "Logout",
            action: () => {
              this.apiClient.unsetAuth();
            }
          }}
        />
        <Container>
          <main className={classes.main}>
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
          </main>
        </Container>
      </MuiThemeProvider>
    );
  }
}

export default withStyles(styles)(App);
