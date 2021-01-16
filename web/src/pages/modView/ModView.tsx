import React from "react";
import {RouteComponentProps, withRouter} from "react-router-dom";
import BoardRender, {ActionableRenderTypes, RenderDataTypes, RenderTypes, Row} from "../../api/BoardRender";
import Button from "./columnRenders/Button";
import Image from "./columnRenders/Image";
import ImageList from "./columnRenders/ImageList";
import Text from "./columnRenders/Text";
import Video from "./columnRenders/Video";
import {
  CircularProgress, FormControlLabel,
  Grid,
  Paper,
  Table,
  TableBody, TableCell,
  TableContainer,
  TableHead, TableRow,
  Typography,
  Switch,
  Checkbox
} from "@material-ui/core";

type Props = RouteComponentProps<{
  name: string;
}>;

interface State {
  loading: boolean;
  error?: Error
  boardRender: BoardRender | {};
  multiActionOn: boolean;
  multiActionSelectedIndexes: Set<number>;
  multiActionLastSelectedIndex: number;
  holdingShift: boolean;
}

class ModView extends React.Component<Props, State> {
  private static InitialState = {
    loading: true,
    boardRender: {},
    multiActionOn: false,
    multiActionSelectedIndexes: new Set<number>(),
    multiActionLastSelectedIndex: -1,
    holdingShift: false,
  };
  private readonly boardId: string;

  constructor(props: Props) {
    super(props);
    this.boardId = decodeURIComponent(this.props.match.params.name);
    this.state = ModView.InitialState;
  }

  loadQuery = () => {
    this.setState(ModView.InitialState);
    this.props.apiClient.renderBoard(this.boardId)
      .then(boardRender => this.setState({ boardRender }))
      .catch(error => {
        this.setState({ error })
      })
      .finally(() => {
        this.setState({ loading: false });
      });
  }

  public componentDidMount() {
    document.addEventListener("keydown", this.keyDown, false);
    document.addEventListener("keyup", this.keyUp, false);
    this.loadQuery();
  }

  public componentWillUnmount(): void {
    document.removeEventListener("keydown", this.keyDown, false);
    document.removeEventListener("keyup", this.keyUp, false);
  }

  public renderCell = (
    type: RenderTypes,
    data: RenderDataTypes,
    rawDocument?: object,
    callbackId?: string,
    getRawDocument?: () => object[],
  ) => {
    let ColumnComponent;
    if (type === "text") {
      ColumnComponent = Text;
    } else if (type === "image") {
      ColumnComponent = Image;
    } else if (type === "image_list") {
      ColumnComponent = ImageList;
    } else if (type === "button") {
      ColumnComponent = Button;
    } else if (type === "video") {
      ColumnComponent = Video;
    }
    if (!ColumnComponent) {
      return <Typography>{`Unknown column type ${type}`}</Typography>;
    }
    return (
      <ColumnComponent
        data={data}
        boardId={this.boardId}
        callbackId={callbackId}
        rawDocument={rawDocument}
        getRawDocument={getRawDocument}
        apiClient={this.props.apiClient}
        reloading={() => {
          this.setState({ loading: true })
        }}
        reload={(boardRender) => {
          this.setState({ boardRender })
        }}
        reloadFinished={() => {
          this.setState({ loading: false })
        }}
      />
    )
  }

  public onToggleRowMultiAction = (index: number) => {
    const newSelectedIndexes = new Set<number>(this.state.multiActionSelectedIndexes.values());
    if (newSelectedIndexes.has(index)) {
      newSelectedIndexes.delete(index);
    } else {
      newSelectedIndexes.add(index);
      const lastSelectedIndex = this.state.multiActionLastSelectedIndex;
      if (this.state.holdingShift
        && lastSelectedIndex !== -1
        && lastSelectedIndex < index
      ) {
        for (let i = lastSelectedIndex; i < index + 1; i++) {
          newSelectedIndexes.add(i);
        }
      }
      this.setState({
        multiActionLastSelectedIndex: index,
      });
    }
    this.setState({
      multiActionSelectedIndexes: newSelectedIndexes,
    });
  }

  public renderRow = (projectionNames: string[], row: Row, rowIndex: number) => {
    const rowRenders = row.renders;
    return (
      <TableRow key={rowIndex}>
        {this.state.multiActionOn ?
          <TableCell
            hidden={!this.state.multiActionOn}
            key="multi-action-selected"
          >
            <Checkbox
              checked={this.state.multiActionSelectedIndexes.has(rowIndex)}
              onChange={() => {
                this.onToggleRowMultiAction(rowIndex);
              }}
            />
          </TableCell> :
          null
        }
        {projectionNames.map((name) => {
          const rowRender = rowRenders[name];
          let cell;
          if (!rowRender) {
            cell = (<Typography>N/A</Typography>);
          } else {
            cell = this.renderCell(
              rowRender.type,
              rowRender.data,
              row.raw_document,
              rowRender.callback_id,
            );
          }
          return (
            <TableCell
              key={name}
            >{cell}</TableCell>
          );
        })}
      </TableRow>
    );
  }

  public renderPayload = () => {
    const boardRender: BoardRender = this.state.boardRender as BoardRender;
    const {payload} = boardRender;
    if (!payload || payload.length === 0) {
      return (
        <Typography>Query is empty</Typography>
      );
    }
    const projectionNames = (this.state.boardRender as BoardRender).board_query.projections.map((p) => p.name);
    return (
      <React.Fragment>
        <FormControlLabel
          label="Toggle multi-action"
          control={
            <Switch
              checked={this.state.multiActionOn}
              onChange={() => {
                this.setState({
                  multiActionOn: !this.state.multiActionOn,
                })
              }}
            />
          }
        />
        <div
          hidden={!this.state.multiActionOn}
          style={{marginBottom: 12}}
        >
          <Typography>
            Selected {this.state.multiActionSelectedIndexes.size} items.&nbsp;
            {
              this.state.holdingShift ?
                `Range selecting`:
                `Hold "shift" to range select`
            }.
          </Typography>
          {this.renderMultiActions()}
        </div>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                {this.state.multiActionOn ?
                  <TableCell
                    key="multi-action-selected"
                  >Multi-action selected</TableCell> :
                  null
                }
                {projectionNames.map(name =>
                  <TableCell
                    key={name}
                  >{name}</TableCell>
                )}
              </TableRow>
            </TableHead>
            <TableBody>
              {payload.map((row, index) => {
                return this.renderRow(projectionNames, row, index);
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </React.Fragment>
    );
  }

  public renderMultiActions = () => {
    const boardRender = (this.state.boardRender as BoardRender);
    const payload = boardRender.payload;
    if (payload.length === 0) {
      return <Typography>No multi-action to render</Typography>;
    }
    const firstRowRenders = payload[0].renders;
    const projectionNames = boardRender.board_query.projections.map((p) => p.name);

    const headings = projectionNames.map((name) =>
      <TableCell key={name}>{name}</TableCell>,
    );

    const columns = projectionNames.map((name) => {
      const render = firstRowRenders[name];
      let cell;
      if (!render) {
        cell = (<Typography>N/A</Typography>);
      } else if (!ActionableRenderTypes.has(render.type)) {
        cell = (<Typography>Not action-able</Typography>);
      } else {
        cell = this.renderCell(
          render.type,
          render.data,
          undefined,
          render.callback_id,
          () => {
            return Array.from(this.state.multiActionSelectedIndexes).map((index) => {
              return payload[index].raw_document;
            });
          },
        );
      }
      return (
        <TableCell key={name}>{cell}</TableCell>
      );
    });
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
          <TableRow>
            {headings}
          </TableRow>
          </TableHead>
          <TableBody>
          <TableRow>
            {columns}
          </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  public keyDown = (e) => {
    if (e.keyCode === 16 && this.state.multiActionOn) {
      this.setState({
        holdingShift: true,
      });
    }
  }

  public keyUp = (e) => {
    if (e.keyCode === 16 && this.state.multiActionOn) {
      this.setState({
        holdingShift: false,
      });
    }
  }

  public render() {
    if (this.state.loading) {
      return (
        <Grid container justify="center">
          <CircularProgress />
        </Grid>
      )
    }
    if (this.state.error) {
      return (
        <Grid container justify="center">
          <Typography variant='body1'>
            Failed to load. Reason: {this.state.error.toString()}
          </Typography>
        </Grid>
      )
    }

    const boardRender: BoardRender = this.state.boardRender as BoardRender;
    return (
      <React.Fragment>
        <Typography>Mod view "{this.boardId}" ({boardRender.count_without_limit})</Typography>
        {this.renderPayload()}
      </React.Fragment>
    );
  }
}

export default withRouter(ModView);
