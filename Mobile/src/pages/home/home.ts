import { Component } from '@angular/core';
import { NavController, NavParams, Platform } from 'ionic-angular';
import { CameraPreview, CameraPreviewOptions, CameraPreviewPictureOptions } from '@ionic-native/camera-preview';
import { DetectorService } from '../../services/rest/DetectorService';
import { NotificationService } from '../../services/device/NotificationService';
import { Subscription } from "rxjs";
import { TimerObservable } from "rxjs/observable/TimerObservable";
import { Device } from '@ionic-native/device';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  private subscription: Subscription;

  constructor(public navCtrl: NavController, public navParams: NavParams, public platform: Platform, public cameraPreview: CameraPreview,
              public detectorService:DetectorService, public notification: NotificationService, private device: Device) {
    this.platform.ready().then(() => {
      var width = 0;
      var height = 0;
      if (this.platform.is('ios')) {
        width = window.screen.height;
        height = window.screen.width;
      } else if(this.platform.is('android')) {
        width = window.screen.width;
        height = window.screen.height;
      }
      const cameraPreviewOpts: CameraPreviewOptions = {
        x: 0,
        y: 0,
        width: width,
        height: height,
        camera: 'rear',
        tapPhoto: false,
        previewDrag: false,
        toBack: false,
        alpha: 1
      };
      console.log(window.screen.width+"x"+window.screen.height+"-"+window.pageYOffset);
      this.cameraPreview.startCamera(cameraPreviewOpts);
      console.log('HomePage startCamera');
      // this.takePicture(detectorService)

    });

  }

  ionViewCanLeave() {
    this.cameraPreview.stopCamera();
    this.navCtrl.pop();
  }


  ngOnInit() {
    let timer = TimerObservable.create(1000, 2000);
    this.subscription = timer.subscribe(t => {
      this.takePicture()
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  takePicture() {
    console.log('Begin startCamera');
    var win = function (r) {
      console.log("Code = " + r.responseCode);
      console.log("Response = " + r.response);
      console.log("Sent = " + r.bytesSent);
      var result = JSON.parse(r.response);
      // console.log(JSON.stringify(result.results[0].predictions[0].labels));
      // alert("American Black Bear : " + result.results[0].predictions[0].labels["American Black Bear"])
      var value;
      var showvalue = JSON.stringify(result.results[0].predictions[0].labels);
      value = result.images[0].classifiers[0].classes[0].score;
      if(value > parseFloat("0.5")) {
         alert(showvalue);
      }
      // value = result.results[0].predictions[0].labels;
      // for (var key in value) {
      //   console.log("key value", key, value[key]);
      //   if(parseFloat(value[key]) > parseFloat("0.5")) {
      //     // console.log(parseFloat(value[key]))
      //     // console.log(value[key]);
      //     // notify.notify_warning(value);
      //     alert(showvalue);
      //     break;
      //   }
      // }

    };

    var fail = function (error) {
      alert("An error has occurred: Code = " + error.code);
      console.log("upload error source " + error.source);
      console.log("upload error target " + error.target);
    };

    this.takePreviewPicture(this.detectorService, win, fail);
  }

  private takePreviewPicture(detectorService, win: (r) => any, fail: (error) => any) {
      this.platform.ready().then(() => {
        const option: CameraPreviewPictureOptions = {width:640, height:1280, quality: 50};
        this.cameraPreview.setFlashMode("off");
        this.cameraPreview.takePicture(function (imgData) {
          console.log('HomePage takePicture');
          const bytes: string = atob(imgData);
          const byteNumbers = new Array(bytes.length);
          for (let i = 0; i < bytes.length; i++) {
            byteNumbers[i] = bytes.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);

          const blob: Blob = new Blob([byteArray], { type: 'image/png' });
          detectorService.detector(blob, win, fail, this.navParams.get("email"), this.device.uuid);
        });

        if (this.platform.is('ios')) {
          this.cameraPreview.takePicture(option).then((imgData) => {
            console.log('HomePage takePicture');
            const bytes: string = atob(imgData);
            const byteNumbers = new Array(bytes.length);
            for (let i = 0; i < bytes.length; i++) {
              byteNumbers[i] = bytes.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);

            const blob: Blob = new Blob([byteArray], {type: 'image/jpeg'});
            detectorService.detector(blob, win, fail, this.navParams.get("email"), this.device.uuid);
          });
        } else if(this.platform.is('android')) {
          this.cameraPreview.takePicture(option).then((imgData) => {
            // this.cameraPreview.takePicture(function(imgData) {
            console.log('HomePage takePicture');
            const bytes: string = atob(imgData);
            const byteNumbers = new Array(bytes.length);
            for (let i = 0; i < bytes.length; i++) {
              byteNumbers[i] = bytes.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);

            const blob: Blob = new Blob([byteArray], {type: 'image/jpeg'});
            detectorService.detector(blob, win, fail);
          });
        }

      });
    }
  }
