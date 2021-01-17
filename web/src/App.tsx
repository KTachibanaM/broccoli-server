import React from 'react';
import { Route, Switch, Redirect, withRouter, RouteComponentProps } from "react-router-dom"
import { Helmet } from "react-helmet";
import { MuiThemeProvider, Container, createStyles, withStyles, createMuiTheme, CssBaseline } from "@material-ui/core";
import { AppNav } from "@k-t-corp/frontend-lib"

import PrivateRoute from "./components/PrivateRoute";
import Workers from "./pages/workers/Workers"
import CreateWorker from "./pages/workers/CreateWorker"
import ModViews from "./pages/modView/ModViews"
import ModView from "./pages/modView/ModView"
import Worker from "./pages/workers/Worker"
import ApiClient from "./api/ApiClient";
import Jobs from "./pages/jobs/Jobs";
import Login from "./pages/Login";

import DashboardIcon from '@material-ui/icons/Dashboard';
import AlarmIcon from '@material-ui/icons/Alarm';
import SettingsIcon from '@material-ui/icons/Settings';

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

type Props = RouteComponentProps

interface State {
  instanceTitle: string
}

class App extends React.Component<Props, State> {
  private readonly apiClient: ApiClient

  constructor(props) {
    super(props);
    this.apiClient = new ApiClient()
    this.state = {
      instanceTitle: 'Untitled'
    }
  }

  componentDidMount() {
    this.apiClient.getInstanceTitle()
      .then(instanceTitle => {
        this.setState({ instanceTitle })
      })
  }

  render() {
    const {classes} = this.props;

    return (
      <MuiThemeProvider theme={theme}>
        <CssBaseline/>
        <Helmet>
          <title>{this.state.instanceTitle}</title>
        </Helmet>
        <AppNav
          title={this.state.instanceTitle}
          items={[
            {
              text: 'Mod Views',
              icon: <DashboardIcon />,
              action: () => {
                this.props.history.push("/modViews/view")
              }
            },
            {
              text: 'Workers',
              icon: <AlarmIcon />,
              action: () => {
                this.props.history.push("/workers/view")
              }
            },
            {
              text: 'Jobs',
              icon: <SettingsIcon />,
              action: () => {
                this.props.history.push("/jobs/view")
              }
            }
          ]}
          rightMostItem={{
            text: "Logout",
            icon: null,
            action: () => {
              this.apiClient.unsetAuth();
              window.location.reload()
            }
          }}
        >
          <Container>
            <main className={classes.main}>
              <Switch>
                <Redirect
                  exact
                  from="/"
                  to="/modViews/view"
                />
                <Route
                  exact
                  path='/login'
                  component={() => {
                    return (<Login apiClient={this.apiClient}/>)
                  }}
                />
                <PrivateRoute
                  path="/modViews/view"
                  apiClient={this.apiClient}
                  render={() => {
                    return (<ModViews apiClient={this.apiClient}/>)
                  }}
                />
                <Route
                  path="/modView/:name"
                  apiClient={this.apiClient}
                  component={() => {
                    return (<ModView apiClient={this.apiClient}/>)
                  }}
                />
                <Route
                  path="/workers/view"
                  apiClient={this.apiClient}
                  component={() => {
                    return (<Workers apiClient={this.apiClient} />)
                  }}
                />
                <Route
                  path="/workers/create"
                  apiClient={this.apiClient}
                  component={() => {
                    return (<CreateWorker apiClient={this.apiClient}/>)
                  }}
                />
                <Route
                  path="/worker/:workerId"
                  apiClient={this.apiClient}
                  component={() => {
                    return (<Worker apiClient={this.apiClient}/>)
                  }}
                />
                <Route
                  path="/jobs/view"
                  apiClient={this.apiClient}
                  component={() => {
                    return (<Jobs apiClient={this.apiClient}/>)
                  }}
                />
              </Switch>
            </main>
          </Container>
        </AppNav>
      </MuiThemeProvider>
    );
  }
}

export default withRouter(withStyles(styles)(App));
